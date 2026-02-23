"""
School Management System — Flask API (Optimized for Vercel)
"""
import sqlite3
import os
import json
import shutil
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuration du chemin de la base de données (Vercel impose /tmp pour l'écriture)
DB_PATH = "/tmp/school.db"

# ── Database Setup ──────────────────────────────────────

def get_conn():
    # On s'assure que la DB est initialisée avant de s'y connecter
    if not os.path.exists(DB_PATH):
        init_db()
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def dict_rows(rows):
    return [dict(r) for r in rows]

def init_db():
    # Si la DB n'existe pas dans /tmp, on crée les tables
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL, last_name TEXT NOT NULL,
            email TEXT UNIQUE, phone TEXT, subject_specialty TEXT
        );
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, grade_level TEXT NOT NULL,
            section TEXT, academic_year TEXT,
            homeroom_teacher_id INTEGER,
            FOREIGN KEY (homeroom_teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
        );
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL, last_name TEXT NOT NULL,
            date_of_birth TEXT, email TEXT UNIQUE, phone TEXT,
            class_id INTEGER,
            enrolled_date TEXT DEFAULT (date('now')),
            FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE SET NULL
        );
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, code TEXT UNIQUE NOT NULL,
            description TEXT, teacher_id INTEGER,
            max_capacity INTEGER DEFAULT 30,
            FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
        );
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL, course_id INTEGER NOT NULL,
            enrolled_date TEXT DEFAULT (date('now')),
            UNIQUE(student_id, course_id),
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enrollment_id INTEGER NOT NULL UNIQUE,
            score REAL CHECK(score >= 0 AND score <= 100),
            letter_grade TEXT, remarks TEXT,
            FOREIGN KEY (enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS parents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL, last_name TEXT NOT NULL,
            email TEXT UNIQUE, phone TEXT, address TEXT
        );
        CREATE TABLE IF NOT EXISTS student_parents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL, parent_id INTEGER NOT NULL,
            relationship TEXT DEFAULT 'Parent',
            UNIQUE(student_id, parent_id),
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (parent_id) REFERENCES parents(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL DEFAULT (date('now')),
            status TEXT NOT NULL CHECK(status IN ('Present','Absent','Late','Excused')),
            remarks TEXT,
            UNIQUE(student_id, date),
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL, course_id INTEGER NOT NULL,
            day_of_week TEXT NOT NULL CHECK(day_of_week IN ('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')),
            start_time TEXT NOT NULL, end_time TEXT NOT NULL, room TEXT,
            FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    conn.close()

def _letter(score):
    if score >= 90: return "A"
    if score >= 80: return "B"
    if score >= 70: return "C"
    if score >= 60: return "D"
    return "F"

# Initialisation forcée au démarrage
init_db()

# ── Endpoints ───────────────────────────────────────────
# (Garde tes routes GET, POST, PUT, DELETE ici, elles sont parfaites)

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "database": "initialized"})

# ... tes autres routes ici ...

# Indispensable pour Vercel
if __name__ == "__main__":
    app.run(debug=True)
