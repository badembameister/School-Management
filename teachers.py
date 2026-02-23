from database import get_connection


def add_teacher(first_name, last_name, email, phone, specialty):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO teachers (first_name, last_name, email, phone, subject_specialty) VALUES (?, ?, ?, ?, ?)",
            (first_name, last_name, email, phone, specialty),
        )
        conn.commit()
        print(f"Teacher '{first_name} {last_name}' added successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def list_teachers():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM teachers ORDER BY last_name, first_name").fetchall()
    conn.close()
    if not rows:
        print("No teachers found.")
        return
    print(f"\n{'ID':<5} {'Name':<25} {'Email':<30} {'Phone':<15} {'Specialty'}")
    print("-" * 90)
    for r in rows:
        print(f"{r['id']:<5} {r['first_name'] + ' ' + r['last_name']:<25} {r['email'] or '':<30} {r['phone'] or '':<15} {r['subject_specialty'] or ''}")


def update_teacher(teacher_id, first_name, last_name, email, phone, specialty):
    conn = get_connection()
    conn.execute(
        "UPDATE teachers SET first_name=?, last_name=?, email=?, phone=?, subject_specialty=? WHERE id=?",
        (first_name, last_name, email, phone, specialty, teacher_id),
    )
    conn.commit()
    conn.close()
    print("Teacher updated.")


def delete_teacher(teacher_id):
    conn = get_connection()
    conn.execute("DELETE FROM teachers WHERE id=?", (teacher_id,))
    conn.commit()
    conn.close()
    print("Teacher deleted.")
