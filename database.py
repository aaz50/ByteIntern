import sqlite3
from datetime import datetime
from typing import List, Dict
import config

class JobDatabase:
    def __init__(self, db_path=config.DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with the jobs table"""
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
        print(f"Database initialized at {self.db_path}")
    
    def is_new_job(self, job_id: str) -> bool:
        """Check if a job ID is new (not in database)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT job_id FROM jobs WHERE job_id = ?', (job_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result is None
    
    def add_job(self, job: Dict):
        """Add a new job to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO jobs 
                (job_id, title, company, location, url, description, posted_date, salary_min, salary_max)
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
            print(f"Added job: {job['title']} at {job['company']}")
        except sqlite3.IntegrityError:
            print(f"Job already exists: {job['id']}")
        finally:
            conn.close()
    
    def mark_as_notified(self, job_id: str):
        """Mark a job as notified"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE jobs SET notified = 1 WHERE job_id = ?', (job_id,))
        conn.commit()
        conn.close()
    
    def get_all_jobs(self) -> List[Dict]:
        """Get all jobs from database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM jobs ORDER BY first_seen DESC')
        rows = cursor.fetchall()
        
        jobs = [dict(row) for row in rows]
        conn.close()
        
        return jobs
    
    def get_job_count(self) -> int:
        """Get total number of jobs tracked"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM jobs')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
