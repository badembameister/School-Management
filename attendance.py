from database import get_connection


VALID_STATUSES = ("Present", "Absent", "Late", "Excused")


def mark_attendance(student_id, date, status, remarks=""):
    if status not in VALID_STATUSES:
        print(f"Invalid status. Choose from: {', '.join(VALID_STATUSES)}")
        return
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM attendance WHERE student_id=? AND date=?",
            (student_id, date),
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE attendance SET status=?, remarks=? WHERE id=?",
                (status, remarks, existing["id"]),
            )
        else:
            conn.execute(
                "INSERT INTO attendance (student_id, date, status, remarks) VALUES (?, ?, ?, ?)",
                (student_id, date, status, remarks),
            )
        conn.commit()
        print(f"Attendance recorded: Student {student_id} — {status} on {date}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def mark_class_attendance(class_id, date):
    """Interactively mark attendance for all students in a class."""
    conn = get_connection()
    students = conn.execute("""
        SELECT id, first_name, last_name
        FROM students WHERE class_id = ?
        ORDER BY last_name, first_name
    """, (class_id,)).fetchall()
    conn.close()

    if not students:
        print("No students in this class.")
        return

    print(f"\nMarking attendance for {date}")
    print("Options: P=Present, A=Absent, L=Late, E=Excused")
    print("-" * 50)

    status_map = {"P": "Present", "A": "Absent", "L": "Late", "E": "Excused"}

    for s in students:
        while True:
            choice = input(f"  {s['first_name']} {s['last_name']} [P/A/L/E]: ").strip().upper()
            if choice in status_map:
                mark_attendance(s["id"], date, status_map[choice])
                break
            print("    Invalid. Use P, A, L, or E.")


def view_attendance_by_student(student_id):
    conn = get_connection()
    student = conn.execute(
        "SELECT first_name, last_name FROM students WHERE id=?", (student_id,)
    ).fetchone()
    if not student:
        print("Student not found.")
        conn.close()
        return

    rows = conn.execute("""
        SELECT date, status, remarks
        FROM attendance
        WHERE student_id = ?
        ORDER BY date DESC
    """, (student_id,)).fetchall()
    conn.close()

    if not rows:
        print(f"No attendance records for {student['first_name']} {student['last_name']}.")
        return

    total = len(rows)
    present = sum(1 for r in rows if r["status"] == "Present")
    absent = sum(1 for r in rows if r["status"] == "Absent")
    late = sum(1 for r in rows if r["status"] == "Late")
    excused = sum(1 for r in rows if r["status"] == "Excused")
    rate = (present + late) / total * 100 if total else 0

    print(f"\nAttendance for {student['first_name']} {student['last_name']}:")
    print(f"  Total: {total} | Present: {present} | Absent: {absent} | Late: {late} | Excused: {excused}")
    print(f"  Attendance rate: {rate:.1f}%\n")
    print(f"{'Date':<14} {'Status':<10} {'Remarks'}")
    print("-" * 45)
    for r in rows:
        print(f"{r['date']:<14} {r['status']:<10} {r['remarks'] or ''}")


def view_attendance_by_class_date(class_id, date):
    conn = get_connection()
    rows = conn.execute("""
        SELECT s.id AS student_id, s.first_name || ' ' || s.last_name AS name,
               a.status, a.remarks
        FROM students s
        LEFT JOIN attendance a ON a.student_id = s.id AND a.date = ?
        WHERE s.class_id = ?
        ORDER BY s.last_name, s.first_name
    """, (date, class_id)).fetchall()
    conn.close()

    if not rows:
        print("No students found in this class.")
        return

    print(f"\nAttendance for class on {date}:")
    print(f"{'ID':<5} {'Name':<25} {'Status':<10} {'Remarks'}")
    print("-" * 55)
    for r in rows:
        status = r["status"] or "Not marked"
        print(f"{r['student_id']:<5} {r['name']:<25} {status:<10} {r['remarks'] or ''}")
