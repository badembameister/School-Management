from database import get_connection


def add_parent(first_name, last_name, email, phone, address):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO parents (first_name, last_name, email, phone, address) VALUES (?, ?, ?, ?, ?)",
            (first_name, last_name, email, phone, address),
        )
        conn.commit()
        print(f"Parent '{first_name} {last_name}' added successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def list_parents():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM parents ORDER BY last_name, first_name").fetchall()
    conn.close()
    if not rows:
        print("No parents found.")
        return
    print(f"\n{'ID':<5} {'Name':<25} {'Email':<30} {'Phone':<15} {'Address'}")
    print("-" * 100)
    for r in rows:
        print(f"{r['id']:<5} {r['first_name'] + ' ' + r['last_name']:<25} {r['email'] or '':<30} {r['phone'] or '':<15} {r['address'] or ''}")


def update_parent(parent_id, first_name, last_name, email, phone, address):
    conn = get_connection()
    conn.execute(
        "UPDATE parents SET first_name=?, last_name=?, email=?, phone=?, address=? WHERE id=?",
        (first_name, last_name, email, phone, address, parent_id),
    )
    conn.commit()
    conn.close()
    print("Parent updated.")


def delete_parent(parent_id):
    conn = get_connection()
    conn.execute("DELETE FROM parents WHERE id=?", (parent_id,))
    conn.commit()
    conn.close()
    print("Parent deleted.")


def link_parent_to_student(parent_id, student_id, relationship="Parent"):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO student_parents (student_id, parent_id, relationship) VALUES (?, ?, ?)",
            (student_id, parent_id, relationship),
        )
        conn.commit()
        print("Parent linked to student.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def unlink_parent_from_student(parent_id, student_id):
    conn = get_connection()
    conn.execute(
        "DELETE FROM student_parents WHERE parent_id=? AND student_id=?",
        (parent_id, student_id),
    )
    conn.commit()
    conn.close()
    print("Parent unlinked from student.")


def list_children_of_parent(parent_id):
    conn = get_connection()
    parent = conn.execute("SELECT first_name, last_name FROM parents WHERE id=?", (parent_id,)).fetchone()
    if not parent:
        print("Parent not found.")
        conn.close()
        return
    rows = conn.execute("""
        SELECT s.id, s.first_name, s.last_name, s.email, sp.relationship,
               cl.name AS class_name
        FROM student_parents sp
        JOIN students s ON sp.student_id = s.id
        LEFT JOIN classes cl ON s.class_id = cl.id
        WHERE sp.parent_id = ?
        ORDER BY s.last_name
    """, (parent_id,)).fetchall()
    conn.close()
    if not rows:
        print(f"No children linked to {parent['first_name']} {parent['last_name']}.")
        return
    print(f"\nChildren of {parent['first_name']} {parent['last_name']}:")
    print(f"{'ID':<5} {'Name':<25} {'Relationship':<15} {'Class':<15} {'Email'}")
    print("-" * 70)
    for r in rows:
        print(f"{r['id']:<5} {r['first_name'] + ' ' + r['last_name']:<25} {r['relationship']:<15} {r['class_name'] or '':<15} {r['email'] or ''}")


def list_parents_of_student(student_id):
    conn = get_connection()
    student = conn.execute("SELECT first_name, last_name FROM students WHERE id=?", (student_id,)).fetchone()
    if not student:
        print("Student not found.")
        conn.close()
        return
    rows = conn.execute("""
        SELECT p.id, p.first_name, p.last_name, p.email, p.phone, sp.relationship
        FROM student_parents sp
        JOIN parents p ON sp.parent_id = p.id
        WHERE sp.student_id = ?
    """, (student_id,)).fetchall()
    conn.close()
    if not rows:
        print(f"No parents linked to {student['first_name']} {student['last_name']}.")
        return
    print(f"\nParents of {student['first_name']} {student['last_name']}:")
    print(f"{'ID':<5} {'Name':<25} {'Relationship':<15} {'Email':<30} {'Phone'}")
    print("-" * 80)
    for r in rows:
        print(f"{r['id']:<5} {r['first_name'] + ' ' + r['last_name']:<25} {r['relationship']:<15} {r['email'] or '':<30} {r['phone'] or ''}")
