"""
School Management System — Flask API
All endpoints served under /api/
"""
import sqlite3, os, json
from flask import Flask, request, jsonify

app = Flask(__name__)

DB_PATH = "/tmp/school.db"


# ── Database ────────────────────────────────────────────

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def dict_rows(rows):
    return [dict(r) for r in rows]


def init_db():
    conn = get_conn()
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


init_db()


def _letter(score):
    if score >= 90: return "A"
    if score >= 80: return "B"
    if score >= 70: return "C"
    if score >= 60: return "D"
    return "F"


# ── Health ──────────────────────────────────────────────

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


# ── Students ────────────────────────────────────────────

@app.route("/api/students", methods=["GET"])
def get_students():
    conn = get_conn()
    rows = conn.execute("""
        SELECT s.*, c.name AS class_name
        FROM students s LEFT JOIN classes c ON s.class_id = c.id
        ORDER BY s.last_name, s.first_name
    """).fetchall()
    conn.close()
    return jsonify(dict_rows(rows))


@app.route("/api/students", methods=["POST"])
def create_student():
    d = request.json
    conn = get_conn()
    try:
        conn.execute("INSERT INTO students (first_name,last_name,date_of_birth,email,phone,class_id) VALUES (?,?,?,?,?,?)",
                     (d["first_name"], d["last_name"], d.get("date_of_birth"), d.get("email"), d.get("phone"), d.get("class_id") or None))
        conn.commit()
        return jsonify({"message": "Student created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


@app.route("/api/students/<int:sid>", methods=["PUT"])
def update_student(sid):
    d = request.json
    conn = get_conn()
    conn.execute("UPDATE students SET first_name=?,last_name=?,date_of_birth=?,email=?,phone=?,class_id=? WHERE id=?",
                 (d["first_name"], d["last_name"], d.get("date_of_birth"), d.get("email"), d.get("phone"), d.get("class_id") or None, sid))
    conn.commit(); conn.close()
    return jsonify({"message": "Student updated"})


@app.route("/api/students/<int:sid>", methods=["DELETE"])
def delete_student(sid):
    conn = get_conn()
    conn.execute("DELETE FROM students WHERE id=?", (sid,))
    conn.commit(); conn.close()
    return jsonify({"message": "Student deleted"})


# ── Teachers ────────────────────────────────────────────

@app.route("/api/teachers", methods=["GET"])
def get_teachers():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM teachers ORDER BY last_name, first_name").fetchall()
    conn.close()
    return jsonify(dict_rows(rows))


@app.route("/api/teachers", methods=["POST"])
def create_teacher():
    d = request.json; conn = get_conn()
    try:
        conn.execute("INSERT INTO teachers (first_name,last_name,email,phone,subject_specialty) VALUES (?,?,?,?,?)",
                     (d["first_name"], d["last_name"], d.get("email"), d.get("phone"), d.get("subject_specialty")))
        conn.commit()
        return jsonify({"message": "Teacher created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


@app.route("/api/teachers/<int:tid>", methods=["PUT"])
def update_teacher(tid):
    d = request.json; conn = get_conn()
    conn.execute("UPDATE teachers SET first_name=?,last_name=?,email=?,phone=?,subject_specialty=? WHERE id=?",
                 (d["first_name"], d["last_name"], d.get("email"), d.get("phone"), d.get("subject_specialty"), tid))
    conn.commit(); conn.close()
    return jsonify({"message": "Teacher updated"})


@app.route("/api/teachers/<int:tid>", methods=["DELETE"])
def delete_teacher(tid):
    conn = get_conn()
    conn.execute("DELETE FROM teachers WHERE id=?", (tid,))
    conn.commit(); conn.close()
    return jsonify({"message": "Teacher deleted"})


# ── Courses ─────────────────────────────────────────────

@app.route("/api/courses", methods=["GET"])
def get_courses():
    conn = get_conn()
    rows = conn.execute("""
        SELECT c.*, t.first_name||' '||t.last_name AS teacher_name
        FROM courses c LEFT JOIN teachers t ON c.teacher_id=t.id ORDER BY c.code
    """).fetchall()
    conn.close()
    return jsonify(dict_rows(rows))


@app.route("/api/courses", methods=["POST"])
def create_course():
    d = request.json; conn = get_conn()
    try:
        conn.execute("INSERT INTO courses (name,code,description,teacher_id,max_capacity) VALUES (?,?,?,?,?)",
                     (d["name"], d["code"], d.get("description"), d.get("teacher_id") or None, d.get("max_capacity") or 30))
        conn.commit()
        return jsonify({"message": "Course created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


@app.route("/api/courses/<int:cid>", methods=["PUT"])
def update_course(cid):
    d = request.json; conn = get_conn()
    conn.execute("UPDATE courses SET name=?,code=?,description=?,teacher_id=?,max_capacity=? WHERE id=?",
                 (d["name"], d["code"], d.get("description"), d.get("teacher_id") or None, d.get("max_capacity") or 30, cid))
    conn.commit(); conn.close()
    return jsonify({"message": "Course updated"})


@app.route("/api/courses/<int:cid>", methods=["DELETE"])
def delete_course(cid):
    conn = get_conn()
    conn.execute("DELETE FROM courses WHERE id=?", (cid,))
    conn.commit(); conn.close()
    return jsonify({"message": "Course deleted"})


# ── Classes ─────────────────────────────────────────────

@app.route("/api/classes", methods=["GET"])
def get_classes():
    conn = get_conn()
    rows = conn.execute("""
        SELECT cl.*, t.first_name||' '||t.last_name AS teacher_name
        FROM classes cl LEFT JOIN teachers t ON cl.homeroom_teacher_id=t.id
        ORDER BY cl.grade_level, cl.section
    """).fetchall()
    conn.close()
    return jsonify(dict_rows(rows))


@app.route("/api/classes", methods=["POST"])
def create_class():
    d = request.json; conn = get_conn()
    try:
        conn.execute("INSERT INTO classes (name,grade_level,section,academic_year,homeroom_teacher_id) VALUES (?,?,?,?,?)",
                     (d["name"], d["grade_level"], d.get("section"), d.get("academic_year"), d.get("homeroom_teacher_id") or None))
        conn.commit()
        return jsonify({"message": "Class created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


@app.route("/api/classes/<int:cid>", methods=["PUT"])
def update_class(cid):
    d = request.json; conn = get_conn()
    conn.execute("UPDATE classes SET name=?,grade_level=?,section=?,academic_year=?,homeroom_teacher_id=? WHERE id=?",
                 (d["name"], d["grade_level"], d.get("section"), d.get("academic_year"), d.get("homeroom_teacher_id") or None, cid))
    conn.commit(); conn.close()
    return jsonify({"message": "Class updated"})


@app.route("/api/classes/<int:cid>", methods=["DELETE"])
def delete_class(cid):
    conn = get_conn()
    conn.execute("DELETE FROM classes WHERE id=?", (cid,))
    conn.commit(); conn.close()
    return jsonify({"message": "Class deleted"})


@app.route("/api/classes/<int:cid>/students", methods=["GET"])
def get_class_students(cid):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM students WHERE class_id=? ORDER BY last_name", (cid,)).fetchall()
    conn.close()
    return jsonify(dict_rows(rows))


# ── Parents ─────────────────────────────────────────────

@app.route("/api/parents", methods=["GET"])
def get_parents():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM parents ORDER BY last_name, first_name").fetchall()
    conn.close()
    return jsonify(dict_rows(rows))


@app.route("/api/parents", methods=["POST"])
def create_parent():
    d = request.json; conn = get_conn()
    try:
        conn.execute("INSERT INTO parents (first_name,last_name,email,phone,address) VALUES (?,?,?,?,?)",
                     (d["first_name"], d["last_name"], d.get("email"), d.get("phone"), d.get("address")))
        conn.commit()
        return jsonify({"message": "Parent created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


@app.route("/api/parents/<int:pid>", methods=["PUT"])
def update_parent(pid):
    d = request.json; conn = get_conn()
    conn.execute("UPDATE parents SET first_name=?,last_name=?,email=?,phone=?,address=? WHERE id=?",
                 (d["first_name"], d["last_name"], d.get("email"), d.get("phone"), d.get("address"), pid))
    conn.commit(); conn.close()
    return jsonify({"message": "Parent updated"})


@app.route("/api/parents/<int:pid>", methods=["DELETE"])
def delete_parent(pid):
    conn = get_conn()
    conn.execute("DELETE FROM parents WHERE id=?", (pid,))
    conn.commit(); conn.close()
    return jsonify({"message": "Parent deleted"})


@app.route("/api/parents/link", methods=["POST"])
def link_parent():
    d = request.json; conn = get_conn()
    try:
        conn.execute("INSERT INTO student_parents (student_id,parent_id,relationship) VALUES (?,?,?)",
                     (d["student_id"], d["parent_id"], d.get("relationship", "Parent")))
        conn.commit()
        return jsonify({"message": "Linked"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


@app.route("/api/parents/unlink", methods=["POST"])
def unlink_parent():
    d = request.json; conn = get_conn()
    conn.execute("DELETE FROM student_parents WHERE student_id=? AND parent_id=?",
                 (d["student_id"], d["parent_id"]))
    conn.commit(); conn.close()
    return jsonify({"message": "Unlinked"})


@app.route("/api/students/<int:sid>/parents", methods=["GET"])
def get_student_parents(sid):
    conn = get_conn()
    rows = conn.execute("""
        SELECT p.*, sp.relationship FROM student_parents sp
        JOIN parents p ON sp.parent_id=p.id WHERE sp.student_id=?
    """, (sid,)).fetchall()
    conn.close()
    return jsonify(dict_rows(rows))


@app.route("/api/parents/<int:pid>/children", methods=["GET"])
def get_parent_children(pid):
    conn = get_conn()
    rows = conn.execute("""
        SELECT s.*, sp.relationship, cl.name AS class_name
        FROM student_parents sp
        JOIN students s ON sp.student_id=s.id
        LEFT JOIN classes cl ON s.class_id=cl.id
        WHERE sp.parent_id=?
    """, (pid,)).fetchall()
    conn.close()
    return jsonify(dict_rows(rows))


# ── Enrollments & Grades ────────────────────────────────

@app.route("/api/enrollments", methods=["GET"])
def get_enrollments():
    course_id = request.args.get("course_id")
    student_id = request.args.get("student_id")
    conn = get_conn()
    if course_id:
        rows = conn.execute("""
            SELECT e.id AS enrollment_id, s.id AS student_id,
                   s.first_name||' '||s.last_name AS student_name,
                   g.score, g.letter_grade, g.remarks AS grade_remarks
            FROM enrollments e JOIN students s ON e.student_id=s.id
            LEFT JOIN grades g ON g.enrollment_id=e.id
            WHERE e.course_id=? ORDER BY s.last_name
        """, (course_id,)).fetchall()
    elif student_id:
        rows = conn.execute("""
            SELECT e.id AS enrollment_id, c.id AS course_id, c.code, c.name AS course_name,
                   g.score, g.letter_grade, g.remarks AS grade_remarks
            FROM enrollments e JOIN courses c ON e.course_id=c.id
            LEFT JOIN grades g ON g.enrollment_id=e.id
            WHERE e.student_id=? ORDER BY c.code
        """, (student_id,)).fetchall()
    else:
        rows = conn.execute("""
            SELECT e.id AS enrollment_id, e.student_id, e.course_id,
                   s.first_name||' '||s.last_name AS student_name,
                   c.code AS course_code, c.name AS course_name,
                   g.score, g.letter_grade
            FROM enrollments e
            JOIN students s ON e.student_id=s.id
            JOIN courses c ON e.course_id=c.id
            LEFT JOIN grades g ON g.enrollment_id=e.id
            ORDER BY c.code, s.last_name
        """).fetchall()
    conn.close()
    return jsonify(dict_rows(rows))


@app.route("/api/enrollments", methods=["POST"])
def create_enrollment():
    d = request.json; conn = get_conn()
    try:
        conn.execute("INSERT INTO enrollments (student_id,course_id) VALUES (?,?)",
                     (d["student_id"], d["course_id"]))
        conn.commit()
        return jsonify({"message": "Enrolled"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


@app.route("/api/enrollments/<int:eid>", methods=["DELETE"])
def delete_enrollment(eid):
    conn = get_conn()
    conn.execute("DELETE FROM enrollments WHERE id=?", (eid,))
    conn.commit(); conn.close()
    return jsonify({"message": "Unenrolled"})


@app.route("/api/grades", methods=["POST"])
def assign_grade():
    d = request.json; conn = get_conn()
    score = float(d["score"])
    letter = _letter(score)
    try:
        existing = conn.execute("SELECT id FROM grades WHERE enrollment_id=?", (d["enrollment_id"],)).fetchone()
        if existing:
            conn.execute("UPDATE grades SET score=?,letter_grade=?,remarks=? WHERE enrollment_id=?",
                         (score, letter, d.get("remarks",""), d["enrollment_id"]))
        else:
            conn.execute("INSERT INTO grades (enrollment_id,score,letter_grade,remarks) VALUES (?,?,?,?)",
                         (d["enrollment_id"], score, letter, d.get("remarks","")))
        conn.commit()
        return jsonify({"message": f"Grade: {score:.1f} ({letter})", "letter_grade": letter})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


# ── Attendance ──────────────────────────────────────────

@app.route("/api/attendance", methods=["GET"])
def get_attendance():
    student_id = request.args.get("student_id")
    class_id = request.args.get("class_id")
    date = request.args.get("date")
    conn = get_conn()
    if student_id:
        rows = conn.execute("""
            SELECT * FROM attendance WHERE student_id=? ORDER BY date DESC
        """, (student_id,)).fetchall()
        data = dict_rows(rows)
        total = len(data)
        present = sum(1 for r in data if r["status"] == "Present")
        late = sum(1 for r in data if r["status"] == "Late")
        absent = sum(1 for r in data if r["status"] == "Absent")
        excused = sum(1 for r in data if r["status"] == "Excused")
        rate = (present + late) / total * 100 if total else 0
        conn.close()
        return jsonify({"records": data, "stats": {"total": total, "present": present, "late": late, "absent": absent, "excused": excused, "rate": round(rate, 1)}})
    elif class_id and date:
        rows = conn.execute("""
            SELECT s.id AS student_id, s.first_name||' '||s.last_name AS name,
                   a.status, a.remarks
            FROM students s LEFT JOIN attendance a ON a.student_id=s.id AND a.date=?
            WHERE s.class_id=? ORDER BY s.last_name
        """, (date, class_id)).fetchall()
        conn.close()
        return jsonify(dict_rows(rows))
    conn.close()
    return jsonify([])


@app.route("/api/attendance", methods=["POST"])
def mark_attendance():
    d = request.json; conn = get_conn()
    try:
        existing = conn.execute("SELECT id FROM attendance WHERE student_id=? AND date=?",
                                (d["student_id"], d["date"])).fetchone()
        if existing:
            conn.execute("UPDATE attendance SET status=?,remarks=? WHERE id=?",
                         (d["status"], d.get("remarks",""), existing["id"]))
        else:
            conn.execute("INSERT INTO attendance (student_id,date,status,remarks) VALUES (?,?,?,?)",
                         (d["student_id"], d["date"], d["status"], d.get("remarks","")))
        conn.commit()
        return jsonify({"message": "Recorded"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


@app.route("/api/attendance/bulk", methods=["POST"])
def bulk_attendance():
    """Mark attendance for multiple students at once."""
    d = request.json  # { "date": "...", "records": [{"student_id":1,"status":"Present"}, ...] }
    conn = get_conn()
    try:
        for rec in d["records"]:
            existing = conn.execute("SELECT id FROM attendance WHERE student_id=? AND date=?",
                                    (rec["student_id"], d["date"])).fetchone()
            if existing:
                conn.execute("UPDATE attendance SET status=?,remarks=? WHERE id=?",
                             (rec["status"], rec.get("remarks",""), existing["id"]))
            else:
                conn.execute("INSERT INTO attendance (student_id,date,status,remarks) VALUES (?,?,?,?)",
                             (rec["student_id"], d["date"], rec["status"], rec.get("remarks","")))
        conn.commit()
        return jsonify({"message": f"Recorded {len(d['records'])} entries"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


# ── Schedules ───────────────────────────────────────────

@app.route("/api/schedules", methods=["GET"])
def get_schedules():
    class_id = request.args.get("class_id")
    student_id = request.args.get("student_id")
    conn = get_conn()
    if student_id:
        student = conn.execute("SELECT class_id FROM students WHERE id=?", (student_id,)).fetchone()
        if not student or not student["class_id"]:
            conn.close()
            return jsonify([])
        class_id = student["class_id"]
    if class_id:
        rows = conn.execute("""
            SELECT s.*, c.name AS course_name, c.code AS course_code,
                   t.first_name||' '||t.last_name AS teacher_name
            FROM schedules s JOIN courses c ON s.course_id=c.id
            LEFT JOIN teachers t ON c.teacher_id=t.id
            WHERE s.class_id=?
            ORDER BY CASE s.day_of_week
                WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6
                WHEN 'Sunday' THEN 7 END, s.start_time
        """, (class_id,)).fetchall()
        conn.close()
        return jsonify(dict_rows(rows))
    conn.close()
    return jsonify([])


@app.route("/api/schedules", methods=["POST"])
def create_schedule():
    d = request.json; conn = get_conn()
    try:
        conn.execute("INSERT INTO schedules (class_id,course_id,day_of_week,start_time,end_time,room) VALUES (?,?,?,?,?,?)",
                     (d["class_id"], d["course_id"], d["day_of_week"], d["start_time"], d["end_time"], d.get("room","")))
        conn.commit()
        return jsonify({"message": "Slot added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


@app.route("/api/schedules/<int:sid>", methods=["DELETE"])
def delete_schedule(sid):
    conn = get_conn()
    conn.execute("DELETE FROM schedules WHERE id=?", (sid,))
    conn.commit(); conn.close()
    return jsonify({"message": "Slot deleted"})


# ── Dashboard stats ─────────────────────────────────────

@app.route("/api/dashboard", methods=["GET"])
def dashboard():
    conn = get_conn()
    stats = {
        "students": conn.execute("SELECT COUNT(*) AS c FROM students").fetchone()["c"],
        "teachers": conn.execute("SELECT COUNT(*) AS c FROM teachers").fetchone()["c"],
        "courses":  conn.execute("SELECT COUNT(*) AS c FROM courses").fetchone()["c"],
        "classes":  conn.execute("SELECT COUNT(*) AS c FROM classes").fetchone()["c"],
        "parents":  conn.execute("SELECT COUNT(*) AS c FROM parents").fetchone()["c"],
        "enrollments": conn.execute("SELECT COUNT(*) AS c FROM enrollments").fetchone()["c"],
    }
    conn.close()
    return jsonify(stats)
