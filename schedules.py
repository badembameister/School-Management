from database import get_connection

DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def add_schedule_slot(class_id, course_id, day_of_week, start_time, end_time, room):
    if day_of_week not in DAYS:
        print(f"Invalid day. Choose from: {', '.join(DAYS)}")
        return
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO schedules (class_id, course_id, day_of_week, start_time, end_time, room) VALUES (?, ?, ?, ?, ?, ?)",
            (class_id, course_id, day_of_week, start_time, end_time, room),
        )
        conn.commit()
        print(f"Schedule slot added: {day_of_week} {start_time}-{end_time}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def list_schedule_by_class(class_id):
    conn = get_connection()
    cls = conn.execute("SELECT name FROM classes WHERE id=?", (class_id,)).fetchone()
    if not cls:
        print("Class not found.")
        conn.close()
        return

    rows = conn.execute("""
        SELECT s.id, s.day_of_week, s.start_time, s.end_time, s.room,
               c.name AS course_name, c.code AS course_code,
               t.first_name || ' ' || t.last_name AS teacher_name
        FROM schedules s
        JOIN courses c ON s.course_id = c.id
        LEFT JOIN teachers t ON c.teacher_id = t.id
        WHERE s.class_id = ?
        ORDER BY
            CASE s.day_of_week
                WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6
                WHEN 'Sunday' THEN 7 END,
            s.start_time
    """, (class_id,)).fetchall()
    conn.close()

    if not rows:
        print(f"No schedule for class '{cls['name']}'.")
        return

    print(f"\nSchedule for '{cls['name']}':")
    print(f"{'ID':<5} {'Day':<12} {'Time':<15} {'Course':<25} {'Teacher':<20} {'Room'}")
    print("-" * 90)
    current_day = ""
    for r in rows:
        day_label = r['day_of_week'] if r['day_of_week'] != current_day else ""
        current_day = r['day_of_week']
        time_str = f"{r['start_time']} - {r['end_time']}"
        print(f"{r['id']:<5} {day_label:<12} {time_str:<15} {r['course_name']:<25} {r['teacher_name'] or '':<20} {r['room'] or ''}")


def delete_schedule_slot(slot_id):
    conn = get_connection()
    conn.execute("DELETE FROM schedules WHERE id=?", (slot_id,))
    conn.commit()
    conn.close()
    print("Schedule slot deleted.")


def view_student_schedule(student_id):
    """View the schedule for a student based on their class assignment."""
    conn = get_connection()
    student = conn.execute(
        "SELECT first_name, last_name, class_id FROM students WHERE id=?",
        (student_id,)
    ).fetchone()
    if not student:
        print("Student not found.")
        conn.close()
        return
    if not student["class_id"]:
        print(f"{student['first_name']} {student['last_name']} is not assigned to a class.")
        conn.close()
        return
    conn.close()
    print(f"\nSchedule for {student['first_name']} {student['last_name']}:")
    list_schedule_by_class(student["class_id"])
