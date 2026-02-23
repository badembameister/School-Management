from database import get_connection


def add_course(name, code, description, teacher_id, max_capacity):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO courses (name, code, description, teacher_id, max_capacity) VALUES (?, ?, ?, ?, ?)",
            (name, code, description, teacher_id or None, max_capacity),
        )
        conn.commit()
        print(f"Course '{name}' ({code}) added successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def list_courses():
    conn = get_connection()
    rows = conn.execute("""
        SELECT c.*, t.first_name || ' ' || t.last_name AS teacher_name
        FROM courses c
        LEFT JOIN teachers t ON c.teacher_id = t.id
        ORDER BY c.code
    """).fetchall()
    conn.close()
    if not rows:
        print("No courses found.")
        return
    print(f"\n{'ID':<5} {'Code':<10} {'Name':<25} {'Teacher':<25} {'Capacity':<10} {'Description'}")
    print("-" * 100)
    for r in rows:
        print(f"{r['id']:<5} {r['code']:<10} {r['name']:<25} {r['teacher_name'] or 'Unassigned':<25} {r['max_capacity']:<10} {r['description'] or ''}")


def update_course(course_id, name, code, description, teacher_id, max_capacity):
    conn = get_connection()
    conn.execute(
        "UPDATE courses SET name=?, code=?, description=?, teacher_id=?, max_capacity=? WHERE id=?",
        (name, code, description, teacher_id or None, max_capacity, course_id),
    )
    conn.commit()
    conn.close()
    print("Course updated.")


def delete_course(course_id):
    conn = get_connection()
    conn.execute("DELETE FROM courses WHERE id=?", (course_id,))
    conn.commit()
    conn.close()
    print("Course deleted.")
