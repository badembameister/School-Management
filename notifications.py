import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database import get_connection

try:
    from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SENDER_NAME
except ImportError:
    SMTP_HOST = SMTP_PORT = SMTP_USER = SMTP_PASSWORD = SENDER_NAME = ""


def _send_email(to_email, subject, body_html):
    """Send an email. Returns True on success, False on failure."""
    if not SMTP_USER or not SMTP_PASSWORD:
        print(f"  [Email skipped — SMTP not configured in config.py]")
        return False

    msg = MIMEMultipart("alternative")
    msg["From"] = f"{SENDER_NAME} <{SMTP_USER}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        print(f"  Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"  Email failed for {to_email}: {e}")
        return False


def _get_parents_for_student(student_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.id, p.first_name, p.last_name, p.email
        FROM parents p
        JOIN student_parents sp ON sp.parent_id = p.id
        WHERE sp.student_id = ?
    """, (student_id,)).fetchall()
    conn.close()
    return rows


def notify_parents_of_grade(enrollment_id, score, letter_grade, remarks):
    """Send grade notification to all parents of the student in this enrollment."""
    conn = get_connection()
    row = conn.execute("""
        SELECT s.id AS student_id, s.first_name || ' ' || s.last_name AS student_name,
               c.name AS course_name, c.code AS course_code
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        JOIN courses c ON e.course_id = c.id
        WHERE e.id = ?
    """, (enrollment_id,)).fetchone()
    conn.close()

    if not row:
        return

    parents = _get_parents_for_student(row["student_id"])
    if not parents:
        print("  No parents linked to this student — no emails sent.")
        return

    subject = f"Grade Report: {row['student_name']} — {row['course_name']}"
    body = f"""
    <html><body>
    <h2>Grade Notification</h2>
    <p>Dear Parent,</p>
    <p>This is to inform you of the latest grade for <strong>{row['student_name']}</strong>:</p>
    <table border="1" cellpadding="8" cellspacing="0">
      <tr><th>Course</th><td>{row['course_name']} ({row['course_code']})</td></tr>
      <tr><th>Score</th><td>{score:.1f} / 100</td></tr>
      <tr><th>Grade</th><td>{letter_grade}</td></tr>
      <tr><th>Remarks</th><td>{remarks or 'N/A'}</td></tr>
    </table>
    <p>Best regards,<br>{SENDER_NAME}</p>
    </body></html>
    """

    sent = 0
    for p in parents:
        if p["email"]:
            if _send_email(p["email"], subject, body):
                sent += 1
    print(f"  Grade notification sent to {sent}/{len(parents)} parent(s).")


def send_schedule_to_parents(student_id):
    """Send the student's class schedule to all linked parents."""
    conn = get_connection()
    student = conn.execute(
        "SELECT id, first_name, last_name, class_id FROM students WHERE id=?",
        (student_id,)
    ).fetchone()

    if not student:
        print("Student not found.")
        conn.close()
        return
    if not student["class_id"]:
        print("Student is not assigned to a class.")
        conn.close()
        return

    cls = conn.execute("SELECT name FROM classes WHERE id=?", (student["class_id"],)).fetchone()
    schedule = conn.execute("""
        SELECT s.day_of_week, s.start_time, s.end_time, s.room,
               c.name AS course_name, c.code AS course_code
        FROM schedules s
        JOIN courses c ON s.course_id = c.id
        WHERE s.class_id = ?
        ORDER BY
            CASE s.day_of_week
                WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6
                WHEN 'Sunday' THEN 7 END,
            s.start_time
    """, (student["class_id"],)).fetchall()
    conn.close()

    if not schedule:
        print("No schedule found for this student's class.")
        return

    parents = _get_parents_for_student(student_id)
    if not parents:
        print("No parents linked to this student.")
        return

    student_name = f"{student['first_name']} {student['last_name']}"
    class_name = cls["name"] if cls else "Unknown"

    rows_html = ""
    for s in schedule:
        rows_html += f"<tr><td>{s['day_of_week']}</td><td>{s['start_time']} - {s['end_time']}</td><td>{s['course_name']} ({s['course_code']})</td><td>{s['room'] or ''}</td></tr>"

    subject = f"Class Schedule: {student_name} — {class_name}"
    body = f"""
    <html><body>
    <h2>Class Schedule</h2>
    <p>Dear Parent,</p>
    <p>Here is the schedule for <strong>{student_name}</strong> (Class: {class_name}):</p>
    <table border="1" cellpadding="8" cellspacing="0">
      <tr><th>Day</th><th>Time</th><th>Course</th><th>Room</th></tr>
      {rows_html}
    </table>
    <p>Best regards,<br>{SENDER_NAME}</p>
    </body></html>
    """

    sent = 0
    for p in parents:
        if p["email"]:
            if _send_email(p["email"], subject, body):
                sent += 1
    print(f"  Schedule sent to {sent}/{len(parents)} parent(s).")
