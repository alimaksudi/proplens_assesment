# Data Processing Pipeline
## Silver Land Properties - CSV Import & Validation

---

## Overview

This document outlines the ETL (Extract, Transform, Load) pipeline for importing property data from CSV into PostgreSQL with validation, cleaning, and error handling.

## CSV Schema Analysis

### Source Columns (15 fields)
```
Project name,No of bedrooms,Completion status (off plan/available),bathrooms,
unit type,developer name,Price (USD),Area (sq mtrs),
Property type (apartment/villa),city,country,completion_date,
features,facilities,Project description
```

### Data Quality Issues Observed

1. **Missing values**: Some properties have NULL bedrooms, prices, or dates
2. **Inconsistent formatting**: 
   - Completion status: "x_available" vs "available" vs "off plan"
   - Dates: Multiple formats (DD-MM-YYYY, YYYY-MM-DD)
3. **JSON fields**: Features/facilities as stringified JSON arrays
4. **Duplicate detection**: Same project name in multiple cities
5. **Text encoding**: Special characters in descriptions

---

## Enhanced Database Schema

### Updated Model (Added Fields)

```python
class Project(models.Model):
    # Original fields
    id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=255, db_index=True)
    developer_name = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, db_index=True)
    country = models.CharField(max_length=2)
    property_type = models.CharField(max_length=50)  # apartment, villa
    bedrooms = models.IntegerField(null=True, blank=True, db_index=True)
    bathrooms = models.IntegerField(null=True, blank=True)
    price_usd = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, db_index=True)
    area_sqm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # NEW FIELDS
    unit_type = models.CharField(max_length=100, null=True, blank=True)  # From CSV
    completion_status = models.CharField(max_length=50, null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    features = models.JSONField(default=list, blank=True)
    facilities = models.JSONField(default=list, blank=True)
    description = models.TextField(null=True, blank=True)
    
    # DATA QUALITY FIELDS
    data_source = models.CharField(max_length=50, default='csv_import')
    import_batch_id = models.CharField(max_length=50, null=True, blank=True)  # Track import runs
    data_quality_score = models.FloatField(default=1.0)  # 0.0-1.0 completeness score
    is_valid = models.BooleanField(default=True)  # Failed validation?
    validation_errors = models.JSONField(default=list, blank=True)  # List of errors
    
    # AUDIT FIELDS
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'projects'
        unique_together = [['project_name', 'city', 'developer_name']]  # Prevent duplicates
        indexes = [
            models.Index(fields=['city', 'bedrooms', 'price_usd']),  # Composite for search
            models.Index(fields=['is_valid']),  # Filter invalid records
        ]
```

---

## ETL Pipeline Architecture

```
┌─────────────────┐
│   CSV File      │
│  (17,318 rows)  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  1. EXTRACT             │
│  - Read CSV             │
│  - Detect encoding      │
│  - Handle large files   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  2. TRANSFORM           │
│  - Validate data types  │
│  - Clean text           │
│  - Normalize values     │
│  - Parse JSON           │
│  - Calculate scores     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  3. LOAD                │
│  - Batch insert (1000)  │
│  - Handle duplicates    │
│  - Log errors           │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  4. VALIDATE            │
│  - Run quality checks   │
│  - Generate report      │
└─────────────────────────┘
```

---

## Implementation

### Command: `import_properties_v2.py`

```python
import csv
import json
import logging
from decimal import Decimal, InvalidOperation
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from django.core.management.base import BaseCommand
from django.db import transaction
from domain.models import Project

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import properties from CSV with validation and cleaning'
    
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
        parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for inserts')
        parser.add_argument('--skip-validation', action='store_true', help='Skip validation checks')
        parser.add_argument('--dry-run', action='store_true', help='Preview without importing')
    
    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        batch_size = options['batch_size']
        skip_validation = options['skip_validation']
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS(f'\n=== Starting CSV Import ==='))
        self.stdout.write(f'File: {csv_file_path}')
        self.stdout.write(f'Batch size: {batch_size}')
        self.stdout.write(f'Dry run: {dry_run}\n')
        
        # Step 1: Extract
        rows = self._extract_csv(csv_file_path)
        self.stdout.write(f'✓ Extracted {len(rows)} rows\n')
        
        # Step 2: Transform
        projects, errors = self._transform_rows(rows, skip_validation)
        self.stdout.write(f'✓ Transformed {len(projects)} valid projects')
        self.stdout.write(f'✗ Found {len(errors)} errors\n')
        
        if dry_run:
            self._print_preview(projects[:5], errors[:10])
            return
        
        # Step 3: Load
        imported_count = self._load_projects(projects, batch_size)
        self.stdout.write(f'✓ Imported {imported_count} projects\n')
        
        # Step 4: Validate
        self._validate_import()
        
        self._print_summary(len(rows), imported_count, len(errors))
    
    def _extract_csv(self, file_path: str) -> List[Dict]:
        """Extract: Read CSV with encoding detection"""
        rows = []
        
        # Try UTF-8 first, fallback to latin-1
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    reader = csv.DictReader(file)
                    rows = list(reader)
                    self.stdout.write(f'✓ Detected encoding: {encoding}')
                    break
            except UnicodeDecodeError:
                continue
        
        if not rows:
            raise Exception("Failed to read CSV with any encoding")
        
        return rows
    
    def _transform_rows(
        self, 
        rows: List[Dict], 
        skip_validation: bool
    ) -> Tuple[List[Dict], List[Dict]]:
        """Transform: Clean, validate, and normalize data"""
        projects = []
        errors = []
        
        for idx, row in enumerate(rows, start=1):
            try:
                # Transform row
                project = self._transform_single_row(row)
                
                # Validate
                if not skip_validation:
                    is_valid, validation_errors = self._validate_project(project)
                    project['is_valid'] = is_valid
                    project['validation_errors'] = validation_errors
                    project['data_quality_score'] = self._calculate_quality_score(project)
                
                projects.append(project)
                
            except Exception as e:
                errors.append({
                    'row': idx,
                    'data': row,
                    'error': str(e)
                })
                logger.error(f"Row {idx} failed: {e}")
        
        return projects, errors
    
    def _transform_single_row(self, row: Dict) -> Dict:
        """Transform a single CSV row"""
        
        # Clean project name
        project_name = row.get('Project name', '').strip()
        
        # Parse bedrooms (handle empty/invalid)
        bedrooms = self._parse_int(row.get('No of bedrooms'))
        bathrooms = self._parse_int(row.get('bathrooms'))
        
        # Parse price (handle commas, decimals)
        price_usd = self._parse_decimal(row.get('Price (USD)'))
        area_sqm = self._parse_decimal(row.get('Area (sq mtrs)'))
        
        # Normalize completion status
        completion_status = self._normalize_completion_status(
            row.get('Completion status (off plan/available)', '')
        )
        
        # Parse date (multiple formats)
        completion_date = self._parse_date(row.get('completion_date'))
        
        # Parse JSON fields (features, facilities)
        features = self._parse_json_array(row.get('features', '[]'))
        facilities = self._parse_json_array(row.get('facilities', '[]'))
        
        # Clean text fields
        description = self._clean_text(row.get('Project description', ''))
        
        return {
            'project_name': project_name,
            'developer_name': row.get('developer name', '').strip(),
            'city': row.get('city', '').strip(),
            'country': row.get('country', '').strip()[:2],  # Max 2 chars
            'property_type': row.get('Property type (apartment/villa)', '').strip().lower(),
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'unit_type': row.get('unit type', '').strip(),
            'price_usd': price_usd,
            'area_sqm': area_sqm,
            'completion_status': completion_status,
            'completion_date': completion_date,
            'features': features,
            'facilities': facilities,
            'description': description,
            'data_source': 'csv_import',
            'import_batch_id': datetime.now().strftime('%Y%m%d_%H%M%S')
        }
    
    def _parse_int(self, value: str) -> Optional[int]:
        """Safely parse integer"""
        if not value or value.strip() == '':
            return None
        try:
            return int(float(value))  # Handle "2.0" format
        except (ValueError, TypeError):
            return None
    
    def _parse_decimal(self, value: str) -> Optional[Decimal]:
        """Safely parse decimal (handles commas)"""
        if not value or value.strip() == '':
            return None
        try:
            # Remove commas: "1,234,567.89" → "1234567.89"
            clean_value = value.replace(',', '')
            return Decimal(clean_value)
        except (InvalidOperation, ValueError, TypeError):
            return None
    
    def _parse_date(self, value: str) -> Optional[datetime]:
        """Parse date with multiple format support"""
        if not value or value.strip() == '':
            return None
        
        formats = [
            '%d-%m-%Y',  # 15-10-2021
            '%Y-%m-%d',  # 2021-10-15
            '%m/%d/%Y',  # 10/15/2021
            '%d/%m/%Y',  # 15/10/2021
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(value.strip(), fmt).date()
            except ValueError:
                continue
        
        return None
    
    def _normalize_completion_status(self, value: str) -> str:
        """Normalize completion status values"""
        value = value.lower().strip()
        
        # Map variations to standard values
        status_map = {
            'x_available': 'available',
            'available': 'available',
            'off plan': 'off_plan',
            'off_plan': 'off_plan',
            'under construction': 'under_construction',
            'completed': 'completed',
        }
        
        return status_map.get(value, value)
    
    def _parse_json_array(self, value: str) -> List[str]:
        """Parse JSON array field"""
        if not value or value.strip() in ('', '[]', '{}'):
            return []
        
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
            return []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ''
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove special characters (keep punctuation)
        # Add more cleaning as needed
        
        return text.strip()
    
    def _validate_project(self, project: Dict) -> Tuple[bool, List[str]]:
        """Validate project data"""
        errors = []
        
        # Required fields
        if not project.get('project_name'):
            errors.append('Missing project_name')
        
        if not project.get('city'):
            errors.append('Missing city')
        
        # Business rules
        if project.get('bedrooms') and project['bedrooms'] > 20:
            errors.append('Bedrooms exceeds reasonable limit (20)')
        
        if project.get('price_usd') and project['price_usd'] < 0:
            errors.append('Price cannot be negative')
        
        if project.get('area_sqm') and project['area_sqm'] < 10:
            errors.append('Area too small (min 10 sqm)')
        
        # Data type validation (already handled in parsing, but double-check)
        if project.get('country') and len(project['country']) > 2:
            errors.append('Country code too long (max 2 chars)')
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def _calculate_quality_score(self, project: Dict) -> float:
        """Calculate data completeness score (0.0 - 1.0)"""
        
        # Important fields and their weights
        fields = {
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
        for field, weight in fields.items():
            value = project.get(field)
            if value and value != [] and value != '':
                score += weight
        
        return round(score, 2)
    
    def _load_projects(self, projects: List[Dict], batch_size: int) -> int:
        """Load: Batch insert projects into database"""
        imported_count = 0
        
        # Process in batches
        for i in range(0, len(projects), batch_size):
            batch = projects[i:i+batch_size]
            
            with transaction.atomic():
                for project_data in batch:
                    try:
                        # Use update_or_create to handle duplicates
                        project, created = Project.objects.update_or_create(
                            project_name=project_data['project_name'],
                            city=project_data['city'],
                            developer_name=project_data['developer_name'],
                            defaults=project_data
                        )
                        
                        if created:
                            imported_count += 1
                    
                    except Exception as e:
                        logger.error(f"Failed to import {project_data['project_name']}: {e}")
            
            self.stdout.write(f'  Processed batch {i//batch_size + 1}... ({imported_count} imported)')
        
        return imported_count
    
    def _validate_import(self):
        """Post-import validation checks"""
        total = Project.objects.count()
        valid = Project.objects.filter(is_valid=True).count()
        invalid = total - valid
        
        avg_quality = Project.objects.aggregate(
            models.Avg('data_quality_score')
        )['data_quality_score__avg'] or 0
        
        self.stdout.write(f'\n=== Import Validation ===')
        self.stdout.write(f'Total projects: {total}')
        self.stdout.write(f'Valid: {valid} ({valid/total*100:.1f}%)')
        self.stdout.write(f'Invalid: {invalid} ({invalid/total*100:.1f}%)')
        self.stdout.write(f'Avg quality score: {avg_quality:.2f}')
    
    def _print_preview(self, projects: List[Dict], errors: List[Dict]):
        """Print preview for dry-run"""
        self.stdout.write('\n=== PREVIEW (First 5 projects) ===')
        
        for project in projects:
            self.stdout.write(f'\n{project["project_name"]}')
            self.stdout.write(f'  City: {project["city"]}')
            self.stdout.write(f'  Bedrooms: {project["bedrooms"]}')
            self.stdout.write(f'  Price: ${project["price_usd"]}')
            self.stdout.write(f'  Quality Score: {project.get("data_quality_score", "N/A")}')
            self.stdout.write(f'  Valid: {project.get("is_valid", "N/A")}')
        
        if errors:
            self.stdout.write(f'\n=== ERRORS (First 10) ===')
            for error in errors:
                self.stdout.write(f'Row {error["row"]}: {error["error"]}')
    
    def _print_summary(self, total_rows: int, imported: int, errors: int):
        """Print final summary"""
        self.stdout.write(self.style.SUCCESS(f'\n=== Import Complete ==='))
        self.stdout.write(f'Total rows: {total_rows}')
        self.stdout.write(f'Successfully imported: {imported} ({imported/total_rows*100:.1f}%)')
        self.stdout.write(f'Errors: {errors} ({errors/total_rows*100:.1f}%)')
```

---

## Usage

### Basic Import
```bash
python manage.py import_properties_v2 data/Property_sales_agent_-_Challenge.csv
```

### With Options
```bash
# Dry run (preview without importing)
python manage.py import_properties_v2 data/properties.csv --dry-run

# Custom batch size
python manage.py import_properties_v2 data/properties.csv --batch-size 500

# Skip validation (faster, use with caution)
python manage.py import_properties_v2 data/properties.csv --skip-validation
```

---

## Data Quality Report

After import, run quality report:

```python
# management/commands/data_quality_report.py

from django.core.management.base import BaseCommand
from domain.models import Project
from django.db.models import Count, Avg, Q

class Command(BaseCommand):
    def handle(self, *args, **options):
        total = Project.objects.count()
        
        # Completeness
        with_bedrooms = Project.objects.exclude(bedrooms__isnull=True).count()
        with_price = Project.objects.exclude(price_usd__isnull=True).count()
        with_description = Project.objects.exclude(description='').count()
        
        # Quality scores
        low_quality = Project.objects.filter(data_quality_score__lt=0.5).count()
        medium_quality = Project.objects.filter(
            data_quality_score__gte=0.5, 
            data_quality_score__lt=0.8
        ).count()
        high_quality = Project.objects.filter(data_quality_score__gte=0.8).count()
        
        # Validation
        invalid = Project.objects.filter(is_valid=False).count()
        
        print(f"""
=== Data Quality Report ===

Total Projects: {total}

Completeness:
  - With Bedrooms: {with_bedrooms} ({with_bedrooms/total*100:.1f}%)
  - With Price: {with_price} ({with_price/total*100:.1f}%)
  - With Description: {with_description} ({with_description/total*100:.1f}%)

Quality Distribution:
  - Low (<0.5): {low_quality} ({low_quality/total*100:.1f}%)
  - Medium (0.5-0.8): {medium_quality} ({medium_quality/total*100:.1f}%)
  - High (>0.8): {high_quality} ({high_quality/total*100:.1f}%)

Validation:
  - Invalid Records: {invalid} ({invalid/total*100:.1f}%)
        """)
```

---

## Best Practices

1. **Always run dry-run first:** Preview data before importing
2. **Use batch processing:** Large CSVs should be processed in batches
3. **Log errors:** Keep track of failed imports for manual review
4. **Validate post-import:** Run quality checks after import completes
5. **Handle duplicates:** Use unique constraints to prevent duplicate imports
6. **Monitor quality scores:** Flag low-quality records for manual review

---

## Troubleshooting

### Issue: Encoding errors
**Solution:** Pipeline tries UTF-8, latin-1, cp1252 automatically

### Issue: Date parsing fails
**Solution:** Add more date formats to `_parse_date()` method

### Issue: JSON fields invalid
**Solution:** Pipeline returns empty array `[]` on parse failure

### Issue: Duplicates detected
**Solution:** Uses `update_or_create` with unique constraint on (project_name, city, developer_name)

---

This ETL pipeline ensures:
- ✅ Clean, validated data in database
- ✅ Error tracking and reporting
- ✅ Data quality scoring
- ✅ Batch processing for performance
- ✅ Duplicate handling
- ✅ Comprehensive logging
