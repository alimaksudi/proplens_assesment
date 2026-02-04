"""
Management command to import properties from CSV with validation and cleaning.

Implements a comprehensive ETL pipeline with:
- Multi-encoding detection
- Data validation and cleaning
- Quality scoring
- Batch processing for performance
- Duplicate handling
"""

import csv
import json
import logging
from decimal import Decimal, InvalidOperation
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from django.core.management.base import BaseCommand
from django.db import transaction
from domain.models import Project

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import properties from CSV file with validation and data quality scoring'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Batch size for database inserts'
        )
        parser.add_argument(
            '--skip-validation',
            action='store_true',
            help='Skip validation checks (faster but less safe)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview import without actually importing'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force import even if properties already exist in database'
        )

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        batch_size = options['batch_size']
        skip_validation = options['skip_validation']
        dry_run = options['dry_run']
        force = options['force']

        # Smart Check: Skip if database is already populated
        if not force and not dry_run:
            existing_count = Project.objects.count()
            if existing_count >= 17000:
                self.stdout.write(self.style.SUCCESS(
                    f'Database already has {existing_count} properties. Skipping auto-import.'
                ))
                self.stdout.write('Use --force to override this check.')
                return

        self.stdout.write(self.style.SUCCESS('\n=== Starting Property CSV Import ==='))
        self.stdout.write(f'File: {csv_file_path}')
        self.stdout.write(f'Batch size: {batch_size}')
        self.stdout.write(f'Dry run: {dry_run}\n')

        # Step 1: Extract
        rows = self._extract_csv(csv_file_path)
        self.stdout.write(self.style.SUCCESS(f'Extracted {len(rows)} rows'))

        # Step 2: Transform
        projects, errors = self._transform_rows(rows, skip_validation)
        self.stdout.write(self.style.SUCCESS(f'Transformed {len(projects)} valid projects'))
        if errors:
            self.stdout.write(self.style.WARNING(f'Found {len(errors)} errors'))

        if dry_run:
            self._print_preview(projects[:5], errors[:10])
            return

        # Step 3: Load
        imported_count, updated_count = self._load_projects(projects, batch_size)
        self.stdout.write(self.style.SUCCESS(
            f'Imported {imported_count} new, updated {updated_count} existing'
        ))

        # Step 4: Validate and report
        self._print_summary(len(rows), imported_count, updated_count, len(errors))

    def _extract_csv(self, file_path: str) -> List[Dict]:
        """
        Extract rows from CSV using a tightened, quote-aware line-signature method.
        """
        import io
        import re
        rows = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            
            if not lines:
                return []
                
            header = [h.strip() for h in lines[0].split(',')]
            data_lines = lines[1:]
            
            records_raw = []
            current_record = []
            
            # Signature check: must have 10+ commas AND data patterns match
            def is_row_start(line):
                # Use a quote-aware split
                f_line = io.StringIO(line)
                reader = csv.reader(f_line)
                try:
                    parts = next(reader)
                except (StopIteration, csv.Error):
                    return False

                if len(parts) < 11:
                    return False

                price = parts[6].strip()
                area = parts[7].strip()
                country = parts[10].strip()
                
                # Numeric check for Price/Area
                is_numeric = (not price or re.match(r'^[0-9. -]+$', price)) and \
                             (not area or re.match(r'^[0-9. -]+$', area))
                
                # Country check (usually 2 uppercase chars)
                is_country = (not country or (len(country) == 2 and country.isupper()))

                return is_numeric and is_country and line.count(',') >= 10

            for line in data_lines:
                if is_row_start(line):
                    if current_record:
                        records_raw.append("".join(current_record))
                    current_record = [line]
                else:
                    current_record.append(line)
                    
            if current_record:
                records_raw.append("".join(current_record))
            
            # Now parse each repaired raw record
            for r in records_raw:
                if r.count('"') % 2 != 0:
                    r = r.strip() + '"\n'
                
                f_record = io.StringIO(r)
                reader = csv.DictReader(f_record, fieldnames=header)
                for row in reader:
                    rows.append(row)
                    
            self.stdout.write(self.style.SUCCESS(f"Ultra-Robust Parser: Extracted {len(rows)} records"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Extraction failed: {e}"))
            
        return rows

    def _transform_rows(
        self,
        rows: List[Dict],
        skip_validation: bool
    ) -> Tuple[List[Dict], List[Dict]]:
        """Transform and validate CSV rows."""
        projects = []
        errors = []
        batch_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        last_valid_project_name = None

        for idx, row in enumerate(rows, start=1):
            try:
                # Inherit project name if missing (common in hierarchical CSVs)
                current_name = self._clean_text(row.get('Project name', ''))
                if not current_name and last_valid_project_name:
                    row['Project name'] = last_valid_project_name
                elif current_name:
                    last_valid_project_name = current_name

                project = self._transform_single_row(row, batch_id)

                if not skip_validation:
                    is_valid, validation_errors = self._validate_project(project)
                    project['is_valid'] = is_valid
                    project['validation_errors'] = validation_errors
                    project['data_quality_score'] = self._calculate_quality_score(project)

                projects.append(project)

            except Exception as e:
                errors.append({
                    'row': idx,
                    'project_name': row.get('Project name', 'Unknown'),
                    'error': str(e)
                })
                logger.warning(f"Row {idx} transformation failed: {e}")

        return projects, errors

    def _transform_single_row(self, row: Dict, batch_id: str) -> Dict[str, Any]:
        """Transform a single CSV row into a project dictionary."""
        project_name = self._clean_text(row.get('Project name', ''))

        # Skip rows without project names
        if not project_name:
            raise ValueError("Missing project name")

        bedrooms = self._parse_int(row.get('No of bedrooms'))
        bathrooms = self._parse_int(row.get('bathrooms'))
        price_usd = self._parse_decimal(row.get('Price (USD)'))
        area_sqm = self._parse_decimal(row.get('Area (sq mtrs)'))
        completion_status = self._normalize_completion_status(
            row.get('Completion status (off plan/available)', '')
        )
        completion_date = self._parse_date(row.get('completion_date'))
        features = self._parse_json_array(row.get('features', '[]'))
        facilities = self._parse_json_array(row.get('facilities', '[]'))
        description = self._clean_text(row.get('Project description', ''))
        property_type = self._normalize_property_type(
            row.get('Property type (apartment/villa)', '')
        )

        return {
            'project_name': project_name,
            'developer_name': self._clean_text(row.get('developer name', '')),
            'city': self._clean_text(row.get('city', '')),
            'country': self._clean_text(row.get('country', ''))[:2],
            'property_type': property_type,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'unit_type': self._clean_text(row.get('unit type', '')),
            'price_usd': price_usd,
            'area_sqm': area_sqm,
            'completion_status': completion_status,
            'completion_date': completion_date,
            'features': features,
            'facilities': facilities,
            'description': description,
            'data_source': 'csv_import',
            'import_batch_id': batch_id,
            'is_valid': True,
            'validation_errors': [],
            'data_quality_score': 1.0,
        }

    def _parse_int(self, value: str) -> Optional[int]:
        """Safely parse integer value."""
        if not value or str(value).strip() == '':
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None

    def _parse_decimal(self, value: str) -> Optional[Decimal]:
        """Safely parse decimal value with comma handling."""
        if not value or str(value).strip() == '':
            return None
        try:
            clean_value = str(value).replace(',', '').strip()
            return Decimal(clean_value)
        except (InvalidOperation, ValueError, TypeError):
            return None

    def _parse_date(self, value: str) -> Optional[datetime]:
        """Parse date with multiple format support."""
        if not value or str(value).strip() == '':
            return None

        formats = [
            '%d-%m-%Y',
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y/%m/%d',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(str(value).strip(), fmt).date()
            except ValueError:
                continue

        return None

    def _normalize_completion_status(self, value: str) -> Optional[str]:
        """Normalize completion status to standard values."""
        if not value:
            return None

        value = str(value).lower().strip()
        status_map = {
            'x_available': 'available',
            'available': 'available',
            'off plan': 'off_plan',
            'off_plan': 'off_plan',
            'under construction': 'under_construction',
            'completed': 'completed',
        }
        return status_map.get(value, value if value else None)

    def _normalize_property_type(self, value: str) -> Optional[str]:
        """Normalize property type to standard values."""
        if not value:
            return None

        value = str(value).lower().strip()
        type_map = {
            'apartment': 'apartment',
            'villa': 'villa',
            'house': 'villa',
            'condo': 'apartment',
            'penthouse': 'apartment',
        }
        return type_map.get(value, value if value else None)

    def _parse_json_array(self, value: str) -> List[str]:
        """Parse JSON array field safely."""
        if not value or str(value).strip() in ('', '[]', '{}'):
            return []

        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if item]
            return []
        except (json.JSONDecodeError, TypeError):
            return []

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ''
        text = ' '.join(str(text).split())
        return text.strip()

    def _validate_project(self, project: Dict) -> Tuple[bool, List[str]]:
        """Validate project data against business rules."""
        errors = []

        if not project.get('project_name'):
            errors.append('Missing project_name')

        if not project.get('city'):
            errors.append('Missing city')

        bedrooms = project.get('bedrooms')
        if bedrooms is not None and (bedrooms < 0 or bedrooms > 20):
            errors.append(f'Invalid bedroom count: {bedrooms}')

        price = project.get('price_usd')
        if price is not None and price < 0:
            errors.append('Price cannot be negative')

        area = project.get('area_sqm')
        if area is not None and area < 5:
            errors.append(f'Area too small: {area} sqm')

        country = project.get('country')
        if country and len(country) > 2:
            errors.append(f'Invalid country code: {country}')

        return len(errors) == 0, errors

    def _calculate_quality_score(self, project: Dict) -> float:
        """Calculate data completeness score (0.0 - 1.0)."""
        weights = {
            'project_name': 0.15,
            'city': 0.15,
            'bedrooms': 0.10,
            'price_usd': 0.15,
            'area_sqm': 0.10,
            'property_type': 0.10,
            'description': 0.10,
            'features': 0.05,
            'facilities': 0.05,
            'completion_date': 0.05,
        }

        score = 0.0
        for field, weight in weights.items():
            value = project.get(field)
            if value and value != [] and value != '':
                score += weight

        return round(score, 2)

    def _load_projects(
        self,
        projects: List[Dict],
        batch_size: int
    ) -> Tuple[int, int]:
        """Load projects into database with batch processing."""
        imported_count = 0
        updated_count = 0

        for i in range(0, len(projects), batch_size):
            batch = projects[i:i + batch_size]

            for project_data in batch:
                try:
                    with transaction.atomic():
                        lookup = {
                            'project_name': project_data['project_name'],
                            'city': project_data['city'],
                            'bedrooms': project_data.get('bedrooms'),
                            'unit_type': project_data.get('unit_type'),
                        }

                        if project_data.get('developer_name'):
                            lookup['developer_name'] = project_data['developer_name']

                        # Using filter().first() instead of get() to handle edge case duplicates gracefully
                        project = Project.objects.filter(**lookup).first()
                        
                        if project:
                            for key, value in project_data.items():
                                setattr(project, key, value)
                            project.save()
                            updated_count += 1
                        else:
                            Project.objects.create(**project_data)
                            imported_count += 1

                except Exception as e:
                    logger.error(
                        f"Failed to import {project_data.get('project_name')}: {e}"
                    )

            batch_num = i // batch_size + 1
            total_batches = (len(projects) + batch_size - 1) // batch_size
            self.stdout.write(
                f'  Batch {batch_num}/{total_batches} processed'
            )

        return imported_count, updated_count

    def _print_preview(self, projects: List[Dict], errors: List[Dict]):
        """Print preview for dry-run mode."""
        self.stdout.write('\n=== PREVIEW (First 5 projects) ===')

        for project in projects:
            self.stdout.write(f"\n{project['project_name']}")
            self.stdout.write(f"  City: {project['city']}")
            self.stdout.write(f"  Bedrooms: {project['bedrooms']}")
            self.stdout.write(f"  Price: ${project['price_usd']}")
            self.stdout.write(f"  Quality Score: {project.get('data_quality_score', 'N/A')}")
            self.stdout.write(f"  Valid: {project.get('is_valid', 'N/A')}")

        if errors:
            self.stdout.write('\n=== ERRORS (First 10) ===')
            for error in errors:
                self.stdout.write(
                    f"Row {error['row']} ({error['project_name']}): {error['error']}"
                )

    def _print_summary(
        self,
        total_rows: int,
        imported: int,
        updated: int,
        errors: int
    ):
        """Print final import summary."""
        self.stdout.write(self.style.SUCCESS('\n=== Import Summary ==='))
        self.stdout.write(f'Total CSV rows: {total_rows}')
        self.stdout.write(f'New projects: {imported}')
        self.stdout.write(f'Updated projects: {updated}')
        self.stdout.write(f'Errors: {errors}')

        if total_rows > 0:
            success_rate = ((imported + updated) / total_rows) * 100
            self.stdout.write(f'Success rate: {success_rate:.1f}%')

        # Database statistics
        total_db = Project.objects.count()
        valid_db = Project.objects.filter(is_valid=True).count()
        self.stdout.write(f'\nDatabase total: {total_db} projects')
        self.stdout.write(f'Valid records: {valid_db}')
