from database import get_connection


def add_class(name, grade_level, section, academic_year, homeroom_teacher_id):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO classes (name, grade_level, section, academic_year, homeroom_teacher_id) VALUES (?, ?, ?, ?, ?)",
            (name, grade_level, section, academic_year, homeroom_teacher_id or None),
        )
        conn.commit()
        print(f"Class '{name}' added successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def list_classes():
    conn = get_connection()
    rows = conn.execute("""
        SELECT c.*, t.first_name || ' ' || t.last_name AS teacher_name
        FROM classes c
        LEFT JOIN teachers t ON c.homeroom_teacher_id = t.id
        ORDER BY c.grade_level, c.section
    """).fetchall()
    conn.close()
    if not rows:
        print("No classes found.")
        return
    print(f"\n{'ID':<5} {'Name':<20} {'Level':<10} {'Section':<10} {'Year':<12} {'Homeroom Teacher'}")
    print("-" * 80)
    for r in rows:
        print(f"{r['id']:<5} {r['name']:<20} {r['grade_level']:<10} {r['section'] or '':<10} {r['academic_year'] or '':<12} {r['teacher_name'] or 'Unassigned'}")


def update_class(class_id, name, grade_level, section, academic_year, homeroom_teacher_id):
    conn = get_connection()
    conn.execute(
        "UPDATE classes SET name=?, grade_level=?, section=?, academic_year=?, homeroom_teacher_id=? WHERE id=?",
        (name, grade_level, section, academic_year, homeroom_teacher_id or None, class_id),
    )
    conn.commit()
    conn.close()
    print("Class updated.")


def delete_class(class_id):
    conn = get_connection()
    conn.execute("DELETE FROM classes WHERE id=?", (class_id,))
    conn.commit()
    conn.close()
    print("Class deleted.")


def assign_student_to_class(student_id, class_id):
    conn = get_connection()
    try:
        conn.execute("UPDATE students SET class_id=? WHERE id=?", (class_id, student_id))
        conn.commit()
        print("Student assigned to class.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def remove_student_from_class(student_id):
    conn = get_connection()
    conn.execute("UPDATE students SET class_id=NULL WHERE id=?", (student_id,))
    conn.commit()
    conn.close()
    print("Student removed from class.")


def list_students_in_class(class_id):
    conn = get_connection()
    cls = conn.execute("SELECT name FROM classes WHERE id=?", (class_id,)).fetchone()
    if not cls:
        print("Class not found.")
        conn.close()
        return
    rows = conn.execute("""
        SELECT id, first_name, last_name, email
        FROM students
        WHERE class_id = ?
        ORDER BY last_name, first_name
    """, (class_id,)).fetchall()
    conn.close()
    if not rows:
        print(f"No students in class '{cls['name']}'.")
        return
    print(f"\nStudents in '{cls['name']}':")
    print(f"{'ID':<5} {'Name':<25} {'Email'}")
    print("-" * 55)
    for r in rows:
        print(f"{r['id']:<5} {r['first_name'] + ' ' + r['last_name']:<25} {r['email'] or ''}")
