"""
School Management System — Flask API
All endpoints served under /api/
"""

import sqlite3
from sqlite3 import IntegrityError
from flask import Flask, request, jsonify

app = Flask(__name__)

DB_PATH = "school.db"


# ─────────────────────────────────────────────
# Database
# ─────────────────────────────────────────────

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def dict_rows(rows):
    return [dict(r) for r in rows]


def init_db():
    conn = get_conn()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        subject_specialty TEXT
    );

    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        grade_level TEXT NOT NULL,
        section TEXT,
        academic_year TEXT,
        homeroom_teacher_id INTEGER,
        FOREIGN KEY (homeroom_teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        date_of_birth TEXT,
        email TEXT UNIQUE,
        phone TEXT,
        class_id INTEGER,
        enrolled_date TEXT DEFAULT (date('now')),
        FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT UNIQUE NOT NULL,
        description TEXT,
        teacher_id INTEGER,
        max_capacity INTEGER DEFAULT 30,
        FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        enrolled_date TEXT DEFAULT (date('now')),
        UNIQUE(student_id, course_id),
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
        FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS grades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        enrollment_id INTEGER NOT NULL UNIQUE,
        score REAL CHECK(score >= 0 AND score <= 100),
        letter_grade TEXT,
        remarks TEXT,
        FOREIGN KEY (enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('Present','Absent','Late','Excused')),
        remarks TEXT,
        UNIQUE(student_id, date),
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );
    """)
    conn.commit()
    conn.close()


init_db()


# ─────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────

def get_json():
    data = request.get_json()
    if not data:
        return None, jsonify({"error": "Invalid or missing JSON body"}), 400
    return data, None, None


def letter_grade(score):
    if score >= 90: return "A"
    if score >= 80: return "B"
    if score >= 70: return "C"
    if score >= 60: return "D"
    return "F"


# ─────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


# ─────────────────────────────────────────────
# Students
# ─────────────────────────────────────────────

@app.route("/api/students", methods=["GET"])
def get_students():
    conn = get_conn()
    rows = conn.execute("""
        SELECT s.*, c.name AS class_name
        FROM students s
        LEFT JOIN classes c ON s.class_id = c.id
        ORDER BY s.last_name, s.first_name
    """).fetchall()
    conn.close()
    return jsonify(dict_rows(rows))


@app.route("/api/students", methods=["POST"])
def create_student():
    d, err, code = get_json()
    if err: return err, code

    if not d.get("first_name") or not d.get("last_name"):
        return jsonify({"error": "first_name and last_name required"}), 400

    conn = get_conn()
    try:
        conn.execute("""
            INSERT INTO students (first_name,last_name,date_of_birth,email,phone,class_id)
            VALUES (?,?,?,?,?,?)
        """, (
            d["first_name"],
            d["last_name"],
            d.get("date_of_birth"),
            d.get("email"),
            d.get("phone"),
            d.get("class_id")
        ))
        conn.commit()
        return jsonify({"message": "Student created"}), 201
    except IntegrityError:
        return jsonify({"error": "Duplicate email or invalid class"}), 400
    finally:
        conn.close()


@app.route("/api/students/<int:sid>", methods=["DELETE"])
def delete_student(sid):
    conn = get_conn()
    cur = conn.execute("DELETE FROM students WHERE id=?", (sid,))
    conn.commit()
    conn.close()

    if cur.rowcount == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student deleted"})


# ─────────────────────────────────────────────
# Teachers
# ─────────────────────────────────────────────

@app.route("/api/teachers", methods=["GET"])
def get_teachers():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM teachers ORDER BY last_name").fetchall()
    conn.close()
    return jsonify(dict_rows(rows))


@app.route("/api/teachers", methods=["POST"])
def create_teacher():
    d, err, code = get_json()
    if err: return err, code

    if not d.get("first_name") or not d.get("last_name"):
        return jsonify({"error": "first_name and last_name required"}), 400

    conn = get_conn()
    try:
        conn.execute("""
            INSERT INTO teachers (first_name,last_name,email,phone,subject_specialty)
            VALUES (?,?,?,?,?)
        """, (
            d["first_name"],
            d["last_name"],
            d.get("email"),
            d.get("phone"),
            d.get("subject_specialty")
        ))
        conn.commit()
        return jsonify({"message": "Teacher created"}), 201
    except IntegrityError:
        return jsonify({"error": "Duplicate email"}), 400
    finally:
        conn.close()


# ─────────────────────────────────────────────
# Enrollments & Grades
# ─────────────────────────────────────────────

@app.route("/api/enrollments", methods=["POST"])
def create_enrollment():
    d, err, code = get_json()
    if err: return err, code

    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO enrollments (student_id,course_id) VALUES (?,?)",
            (d["student_id"], d["course_id"])
        )
        conn.commit()
        return jsonify({"message": "Enrolled"}), 201
    except IntegrityError:
        return jsonify({"error": "Already enrolled or invalid ID"}), 400
    finally:
        conn.close()


@app.route("/api/grades", methods=["POST"])
def assign_grade():
    d, err, code = get_json()
    if err: return err, code

    try:
        score = float(d["score"])
    except:
        return jsonify({"error": "Valid score required"}), 400

    if score < 0 or score > 100:
        return jsonify({"error": "Score must be 0-100"}), 400

    conn = get_conn()
    letter = letter_grade(score)

    try:
        conn.execute("""
            INSERT OR REPLACE INTO grades (enrollment_id,score,letter_grade,remarks)
            VALUES (?,?,?,?)
        """, (
            d["enrollment_id"],
            score,
            letter,
            d.get("remarks","")
        ))
        conn.commit()
        return jsonify({"message": "Grade recorded", "letter": letter})
    except IntegrityError:
        return jsonify({"error": "Invalid enrollment"}), 400
    finally:
        conn.close()


# ─────────────────────────────────────────────
# Attendance
# ─────────────────────────────────────────────

@app.route("/api/attendance", methods=["POST"])
def mark_attendance():
    d, err, code = get_json()
    if err: return err, code

    valid_status = {"Present","Absent","Late","Excused"}
    if d.get("status") not in valid_status:
        return jsonify({"error": "Invalid status"}), 400

    conn = get_conn()
    try:
        conn.execute("""
            INSERT OR REPLACE INTO attendance (student_id,date,status,remarks)
            VALUES (?,?,?,?)
        """, (
            d["student_id"],
            d["date"],
            d["status"],
            d.get("remarks","")
        ))
        conn.commit()
        return jsonify({"message": "Attendance recorded"})
    except IntegrityError:
        return jsonify({"error": "Invalid student"}), 400
    finally:
        conn.close()


# ─────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────

@app.route("/api/dashboard")
def dashboard():
    conn = get_conn()
    stats = {
        "students": conn.execute("SELECT COUNT(*) c FROM students").fetchone()["c"],
        "teachers": conn.execute("SELECT COUNT(*) c FROM teachers").fetchone()["c"],
        "courses": conn.execute("SELECT COUNT(*) c FROM courses").fetchone()["c"],
        "classes": conn.execute("SELECT COUNT(*) c FROM classes").fetchone()["c"],
        "enrollments": conn.execute("SELECT COUNT(*) c FROM enrollments").fetchone()["c"]
    }
    conn.close()
    return jsonify(stats)


# ─────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)
