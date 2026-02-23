from database import get_connection


def _letter_grade(score):
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    return "F"


def enroll_student(student_id, course_id):
    conn = get_connection()
    try:
        # Check capacity
        course = conn.execute("SELECT * FROM courses WHERE id=?", (course_id,)).fetchone()
        if not course:
            print("Course not found.")
            return
        count = conn.execute(
            "SELECT COUNT(*) as cnt FROM enrollments WHERE course_id=?", (course_id,)
        ).fetchone()["cnt"]
        if count >= course["max_capacity"]:
            print(f"Course '{course['name']}' is full ({course['max_capacity']} students).")
            return
        conn.execute(
            "INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)",
            (student_id, course_id),
        )
        conn.commit()
        print("Student enrolled successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def unenroll_student(student_id, course_id):
    conn = get_connection()
    conn.execute(
        "DELETE FROM enrollments WHERE student_id=? AND course_id=?",
        (student_id, course_id),
    )
    conn.commit()
    conn.close()
    print("Student unenrolled.")


def list_enrollments_by_course(course_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT e.id AS enrollment_id, s.id AS student_id,
               s.first_name || ' ' || s.last_name AS student_name,
               g.score, g.letter_grade
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        LEFT JOIN grades g ON g.enrollment_id = e.id
        WHERE e.course_id = ?
        ORDER BY s.last_name
    """, (course_id,)).fetchall()
    conn.close()
    if not rows:
        print("No students enrolled in this course.")
        return
    print(f"\n{'Enroll ID':<12} {'Student ID':<12} {'Name':<25} {'Score':<8} {'Grade'}")
    print("-" * 70)
    for r in rows:
        score = f"{r['score']:.1f}" if r['score'] is not None else "N/A"
        grade = r['letter_grade'] or "N/A"
        print(f"{r['enrollment_id']:<12} {r['student_id']:<12} {r['student_name']:<25} {score:<8} {grade}")


def list_enrollments_by_student(student_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT c.code, c.name AS course_name, g.score, g.letter_grade
        FROM enrollments e
        JOIN courses c ON e.course_id = c.id
        LEFT JOIN grades g ON g.enrollment_id = e.id
        WHERE e.student_id = ?
        ORDER BY c.code
    """, (student_id,)).fetchall()
    conn.close()
    if not rows:
        print("Student is not enrolled in any courses.")
        return
    print(f"\n{'Code':<10} {'Course':<25} {'Score':<8} {'Grade'}")
    print("-" * 55)
    for r in rows:
        score = f"{r['score']:.1f}" if r['score'] is not None else "N/A"
        grade = r['letter_grade'] or "N/A"
        print(f"{r['code']:<10} {r['course_name']:<25} {score:<8} {grade}")


def assign_grade(enrollment_id, score, remarks=""):
    conn = get_connection()
    letter = _letter_grade(score)
    try:
        existing = conn.execute(
            "SELECT id FROM grades WHERE enrollment_id=?", (enrollment_id,)
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE grades SET score=?, letter_grade=?, remarks=? WHERE enrollment_id=?",
                (score, letter, remarks, enrollment_id),
            )
        else:
            conn.execute(
                "INSERT INTO grades (enrollment_id, score, letter_grade, remarks) VALUES (?, ?, ?, ?)",
                (enrollment_id, score, letter, remarks),
            )
        conn.commit()
        print(f"Grade assigned: {score:.1f} ({letter})")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
