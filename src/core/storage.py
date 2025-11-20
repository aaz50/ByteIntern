"""
Storage module - abstracts database operations.

Supports both SQLite (local/GitHub Actions) and DynamoDB (AWS Lambda).
This abstraction makes it easy to swap databases without changing business logic.
"""

import sqlite3
from typing import List, Dict, Protocol
from datetime import datetime
from src.core import config


class StorageInterface(Protocol):
    """Interface that all storage implementations must follow."""
    
    def init_database(self) -> None: ...
    def is_new_job(self, job_id: str) -> bool: ...
    def add_job(self, job: Dict) -> None: ...
    def mark_as_notified(self, job_id: str) -> None: ...
    def get_all_jobs(self) -> List[Dict]: ...
    def get_job_count(self) -> int: ...


class SQLiteStorage:
    """SQLite implementation for local development and GitHub Actions."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self) -> None:
        """Initialize the database with the jobs table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT,
                url TEXT NOT NULL,
                description TEXT,
                posted_date TEXT,
                salary_min REAL,
                salary_max REAL,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notified BOOLEAN DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✓ Database initialized at {self.db_path}")
    
    def is_new_job(self, job_id: str) -> bool:
        """Check if a job ID is new (not in database)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT job_id FROM jobs WHERE job_id = ?', (job_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result is None
    
    def add_job(self, job: Dict) -> None:
        """Add a new job to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO jobs 
                (job_id, title, company, location, url, description, 
                 posted_date, salary_min, salary_max)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job['id'],
                job['title'],
                job['company'],
                job.get('location', ''),
                job['url'],
                job.get('description', ''),
                job.get('posted_date', ''),
                job.get('salary_min'),
                job.get('salary_max')
            ))
            
            conn.commit()
            print(f"  + Added: {job['title']} at {job['company']}")
        except sqlite3.IntegrityError:
            # Job already exists (shouldn't happen if is_new_job is checked)
            pass
        finally:
            conn.close()
    
    def mark_as_notified(self, job_id: str) -> None:
        """Mark a job as having been notified."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE jobs SET notified = 1 WHERE job_id = ?', (job_id,))
        conn.commit()
        conn.close()
    
    def get_all_jobs(self) -> List[Dict]:
        """Get all jobs from database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM jobs ORDER BY first_seen DESC')
        rows = cursor.fetchall()
        
        jobs = [dict(row) for row in rows]
        conn.close()
        
        return jobs
    
    def get_job_count(self) -> int:
        """Get total number of jobs tracked."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM jobs')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count


class DynamoDBStorage:
    """
    DynamoDB implementation for AWS Lambda.
    
    This is a placeholder for future implementation.
    When you're ready to migrate to Lambda, implement these methods
    using boto3 and DynamoDB client.
    """
    
    def __init__(self, table_name: str, region: str):
        self.table_name = table_name
        self.region = region
        # TODO: Initialize boto3 DynamoDB client
        raise NotImplementedError(
            "DynamoDB storage not yet implemented. "
            "Use DB_TYPE=sqlite for now."
        )
    
    def init_database(self) -> None:
        # DynamoDB tables are created via IaC (Terraform/CloudFormation)
        pass
    
    def is_new_job(self, job_id: str) -> bool:
        # TODO: DynamoDB GetItem operation
        raise NotImplementedError()
    
    def add_job(self, job: Dict) -> None:
        # TODO: DynamoDB PutItem operation
        raise NotImplementedError()
    
    def mark_as_notified(self, job_id: str) -> None:
        # TODO: DynamoDB UpdateItem operation
        raise NotImplementedError()
    
    def get_all_jobs(self) -> List[Dict]:
        # TODO: DynamoDB Scan operation
        raise NotImplementedError()
    
    def get_job_count(self) -> int:
        # TODO: DynamoDB Scan with count
        raise NotImplementedError()


def get_storage() -> StorageInterface:
    """
    Factory function to get the appropriate storage implementation.
    
    Returns storage instance based on configuration.
    This is the only function you need to call - it handles the switching.
    """
    db_config = config.get_db_config()
    
    if db_config['type'] == 'sqlite':
        return SQLiteStorage(db_config['path'])
    elif db_config['type'] == 'dynamodb':
        return DynamoDBStorage(
            db_config['table_name'], 
            db_config['region']
        )
    else:
        raise ValueError(f"Unknown database type: {db_config['type']}")
