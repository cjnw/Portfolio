import sqlite3
import os
from pathlib import Path

class Database:
    def __init__(self, app):
        self.app = app
        self.db_path = app.config['DATABASE_PATH']
        
    def get_db(self):
        db = sqlite3.connect(self.db_path)
        db.row_factory = sqlite3.Row
        return db
        
    def init_db(self):
        db = self.get_db()
        cursor = db.cursor()
        
        try:
            # Execute schema files
            schema_dir = Path(__file__).parent / 'create_tables' / 'schema'
            for schema_file in sorted(schema_dir.glob('*.sql')):  # Sort to ensure consistent order
                print(f"Executing schema file: {schema_file}")
                with open(schema_file) as f:
                    cursor.executescript(f.read())
            
            # Verify tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print("Existing tables:", [table['name'] for table in tables])
            
            db.commit()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    def execute_query(self, query_name, params=()):
        db = self.get_db()
        cursor = db.cursor()
        
        # Find and execute the named query
        queries_dir = Path(__file__).parent / 'create_tables' / 'queries'
        for query_file in queries_dir.glob('*.sql'):
            with open(query_file) as f:
                queries = f.read().split('\n\n')
                for query in queries:
                    if query.strip().startswith(f'-- name: {query_name}'):
                        sql = query.split('\n', 1)[1].strip()
                        cursor.execute(sql, params)
                        break
        
        result = cursor.fetchall()
        db.commit()
        db.close()
        return result

    def execute_query_one(self, query_name, params=()):
        result = self.execute_query(query_name, params)
        return result[0] if result else None
