import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "student_performance"),
}

SCHEMA = [
"""CREATE TABLE IF NOT EXISTS students (
 student_id INT AUTO_INCREMENT PRIMARY KEY,
 roll_no VARCHAR(30) NOT NULL UNIQUE,
 name VARCHAR(120) NOT NULL,
 section VARCHAR(30) NOT NULL
)""",
"""CREATE TABLE IF NOT EXISTS subjects (
 subject_id INT AUTO_INCREMENT PRIMARY KEY,
 subject_name VARCHAR(120) NOT NULL UNIQUE,
 max_marks DECIMAL(7,2) NOT NULL,
 pass_marks DECIMAL(7,2) NOT NULL,
 CHECK (max_marks > 0),
 CHECK (pass_marks >= 0 AND pass_marks <= max_marks)
)""",
"""CREATE TABLE IF NOT EXISTS marks (
 mark_id INT AUTO_INCREMENT PRIMARY KEY,
 student_id INT NOT NULL,
 subject_id INT NOT NULL,
 assessment VARCHAR(80) NOT NULL DEFAULT 'Internal',
 marks_obtained DECIMAL(7,2) NOT NULL,
 CONSTRAINT fk_marks_student FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
 CONSTRAINT fk_marks_subject FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
 CONSTRAINT uq_mark UNIQUE (student_id, subject_id, assessment)
)"""
]

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def initialize_database():
    # Database itself must exist before this connection is made.
    conn = get_connection()
    try:
        cur = conn.cursor()
        for statement in SCHEMA:
            cur.execute(statement)
        conn.commit()
        cur.close()
    finally:
        conn.close()
