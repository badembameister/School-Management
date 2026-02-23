from database import get_connection


def add_student(first_name, last_name, dob, email, phone):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO students (first_name, last_name, date_of_birth, email, phone) VALUES (?, ?, ?, ?, ?)",
            (first_name, last_name, dob, email, phone),
        )
        conn.commit()
        print(f"Student '{first_name} {last_name}' added successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def list_students():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM students ORDER BY last_name, first_name").fetchall()
    conn.close()
    if not rows:
        print("No students found.")
        return
    print(f"\n{'ID':<5} {'Name':<25} {'DOB':<12} {'Email':<30} {'Phone':<15} {'Enrolled'}")
    print("-" * 100)
    for r in rows:
        print(f"{r['id']:<5} {r['first_name'] + ' ' + r['last_name']:<25} {r['date_of_birth'] or '':<12} {r['email'] or '':<30} {r['phone'] or '':<15} {r['enrolled_date']}")


def search_students(keyword):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM students WHERE first_name LIKE ? OR last_name LIKE ? OR email LIKE ?",
        (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"),
    ).fetchall()
    conn.close()
    if not rows:
        print("No matching students found.")
        return
    for r in rows:
        print(f"  [{r['id']}] {r['first_name']} {r['last_name']} — {r['email']}")


def update_student(student_id, first_name, last_name, dob, email, phone):
    conn = get_connection()
    conn.execute(
        "UPDATE students SET first_name=?, last_name=?, date_of_birth=?, email=?, phone=? WHERE id=?",
        (first_name, last_name, dob, email, phone, student_id),
    )
    conn.commit()
    conn.close()
    print("Student updated.")


def delete_student(student_id):
    conn = get_connection()
    conn.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()
    print("Student deleted.")
