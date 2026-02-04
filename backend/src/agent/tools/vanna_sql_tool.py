"""
Vanna AI Text-to-SQL tool for natural language property queries.

Uses ChromaDB for training data storage and OpenAI for SQL generation.
"""

import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Vanna requires specific imports
try:
    from vanna.openai import OpenAI_Chat
    from vanna.chromadb import ChromaDB_VectorStore
    VANNA_AVAILABLE = True
except ImportError:
    VANNA_AVAILABLE = False
    logger.warning("Vanna not available. Text-to-SQL will use fallback.")


class VannaSQLTool:
    """
    Text-to-SQL tool using Vanna AI with ChromaDB for training data storage.

    Converts natural language queries to SQL and executes them against
    the property database.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Vanna SQL tool.

        Args:
            config: Configuration dictionary with api_key, model, and path
        """
        self.config = config or {}
        self.vanna = None
        self.is_trained = False

        if VANNA_AVAILABLE:
            self._initialize_vanna()

    def _initialize_vanna(self):
        """Initialize Vanna with OpenAI and ChromaDB."""
        try:
            # Create a custom Vanna class combining vector store and LLM
            class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
                def __init__(self, config=None):
                    ChromaDB_VectorStore.__init__(self, config=config)
                    OpenAI_Chat.__init__(self, config=config)

            vanna_config = {
                'api_key': self.config.get('api_key') or os.getenv('OPENAI_API_KEY'),
                'model': self.config.get('model') or os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                'path': self.config.get('path') or os.getenv('CHROMA_PERSIST_DIR', './chroma_db'),
            }

            self.vanna = MyVanna(config=vanna_config)
            logger.info("Vanna SQL tool initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Vanna: {e}")
            self.vanna = None

    def connect_to_database(self):
        """Connect Vanna to PostgreSQL database."""
        if not self.vanna:
            return False

        try:
            self.vanna.connect_to_postgres(
                host=os.getenv('DB_HOST', 'localhost'),
                dbname=os.getenv('DB_NAME', 'silver_land_db'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'postgres'),
                port=int(os.getenv('DB_PORT', 5432))
            )
            logger.info("Vanna connected to PostgreSQL")
            return True
        except Exception as e:
            logger.error(f"Failed to connect Vanna to database: {e}")
            return False

    def train(self):
        """Train Vanna with DDL and example queries."""
        if not self.vanna:
            return

        try:
            # Train with DDL
            ddl = """
            CREATE TABLE projects (
                id SERIAL PRIMARY KEY,
                project_name VARCHAR(255) NOT NULL,
                developer_name VARCHAR(255),
                city VARCHAR(100) NOT NULL,
                country VARCHAR(2) NOT NULL,
                property_type VARCHAR(50),
                bedrooms INTEGER,
                bathrooms INTEGER,
                price_usd DECIMAL(12, 2),
                area_sqm DECIMAL(10, 2),
                completion_status VARCHAR(50),
                completion_date DATE,
                features JSONB,
                facilities JSONB,
                description TEXT,
                is_valid BOOLEAN DEFAULT TRUE
            );
            """
            self.vanna.train(ddl=ddl)
            logger.info("Trained Vanna with DDL")

            # Train with example queries
            examples = self._get_training_examples()
            for example in examples:
                try:
                    self.vanna.train(
                        question=example["question"],
                        sql=example["sql"]
                    )
                except Exception as e:
                    logger.warning(f"Failed to train example: {e}")

            self.is_trained = True
            logger.info(f"Trained Vanna with {len(examples)} examples")

        except Exception as e:
            logger.error(f"Error training Vanna: {e}")

    def _get_training_examples(self) -> List[Dict[str, str]]:
        """Get SQL training examples."""
        return [
            {
                "question": "Show me 2-bedroom apartments in Chicago",
                "sql": "SELECT * FROM projects WHERE bedrooms = 2 AND city ILIKE '%Chicago%' AND property_type = 'apartment' AND is_valid = TRUE ORDER BY price_usd"
            },
            {
                "question": "What properties are under $1 million?",
                "sql": "SELECT * FROM projects WHERE price_usd < 1000000 AND is_valid = TRUE ORDER BY price_usd"
            },
            {
                "question": "Find 3-bedroom properties in Chicago under $2 million",
                "sql": "SELECT * FROM projects WHERE bedrooms = 3 AND city ILIKE '%Chicago%' AND price_usd < 2000000 AND is_valid = TRUE"
            },
            {
                "question": "Show me available properties",
                "sql": "SELECT * FROM projects WHERE completion_status = 'available' AND is_valid = TRUE"
            },
            {
                "question": "What apartments are in Singapore?",
                "sql": "SELECT * FROM projects WHERE (city ILIKE '%Singapore%' OR country = 'SG') AND property_type = 'apartment' AND is_valid = TRUE"
            },
            {
                "question": "Show me villas under $5 million",
                "sql": "SELECT * FROM projects WHERE property_type = 'villa' AND price_usd < 5000000 AND is_valid = TRUE"
            },
            {
                "question": "What are the cheapest 1-bedroom apartments?",
                "sql": "SELECT * FROM projects WHERE bedrooms = 1 AND property_type = 'apartment' AND is_valid = TRUE ORDER BY price_usd LIMIT 10"
            },
            {
                "question": "Show me properties with 2 to 3 bedrooms between $500k and $1M",
                "sql": "SELECT * FROM projects WHERE bedrooms BETWEEN 2 AND 3 AND price_usd BETWEEN 500000 AND 1000000 AND is_valid = TRUE"
            },
            {
                "question": "Find luxury apartments over $2 million",
                "sql": "SELECT * FROM projects WHERE property_type = 'apartment' AND price_usd > 2000000 AND is_valid = TRUE ORDER BY price_usd DESC"
            },
            {
                "question": "Show me off-plan properties in Dubai",
                "sql": "SELECT * FROM projects WHERE completion_status = 'off_plan' AND city ILIKE '%Dubai%' AND is_valid = TRUE"
            },
        ]

    async def query_properties(self, natural_language_query: str) -> List[Dict]:
        """
        Convert natural language to SQL and execute query.

        Args:
            natural_language_query: User's search criteria in natural language

        Returns:
            List of matching properties as dictionaries
        """
        if not self.vanna:
            logger.warning("Vanna not available, using fallback")
            return []

        try:
            sql = self.vanna.generate_sql(natural_language_query)
            logger.info(f"Generated SQL: {sql}")

            results = self.vanna.run_sql(sql)

            if hasattr(results, 'to_dict'):
                return results.to_dict('records')
            elif isinstance(results, list):
                return results
            else:
                return []

        except Exception as e:
            logger.error(f"Vanna query failed: {e}")
            return []

    def generate_sql(self, query: str) -> str:
        """Generate SQL without executing (for debugging)."""
        if not self.vanna:
            return ""

        try:
            return self.vanna.generate_sql(query)
        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            return ""


# Singleton instance
_vanna_instance: Optional[VannaSQLTool] = None


def get_vanna_tool() -> VannaSQLTool:
    """Get or create Vanna tool singleton."""
    global _vanna_instance

    if _vanna_instance is None:
        _vanna_instance = VannaSQLTool()

    return _vanna_instance
