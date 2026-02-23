"""
School Management System
========================
A CLI application to manage students, teachers, courses,
enrollments, and grades using SQLite.
"""

import sys
from database import init_db
from students import add_student, list_students, search_students, update_student, delete_student
from teachers import add_teacher, list_teachers, update_teacher, delete_teacher
from courses import add_course, list_courses, update_course, delete_course
from classes import (
    add_class, list_classes, update_class, delete_class,
    assign_student_to_class, remove_student_from_class, list_students_in_class,
)
from enrollments import (
    enroll_student, unenroll_student,
    list_enrollments_by_course, list_enrollments_by_student,
    assign_grade,
)
from parents import (
    add_parent, list_parents, update_parent, delete_parent,
    link_parent_to_student, unlink_parent_from_student,
    list_children_of_parent, list_parents_of_student,
)
from attendance import (
    mark_attendance, mark_class_attendance,
    view_attendance_by_student, view_attendance_by_class_date,
)
from schedules import (
    add_schedule_slot, list_schedule_by_class, delete_schedule_slot,
    view_student_schedule,
)
from notifications import send_schedule_to_parents


def input_int(prompt, allow_empty=False):
    while True:
        val = input(prompt).strip()
        if allow_empty and val == "":
            return None
        try:
            return int(val)
        except ValueError:
            print("Please enter a valid number.")


def input_float(prompt):
    while True:
        val = input(prompt).strip()
        try:
            return float(val)
        except ValueError:
            print("Please enter a valid number.")


# ── Menus ────────────────────────────────────────────────

def student_menu():
    while True:
        print("\n--- Student Management ---")
        print("1. Add Student")
        print("2. List All Students")
        print("3. Search Students")
        print("4. Update Student")
        print("5. Delete Student")
        print("6. View Student Transcript")
        print("0. Back")
        choice = input("Choose: ").strip()

        if choice == "1":
            fn = input("First name: ").strip()
            ln = input("Last name: ").strip()
            dob = input("Date of birth (YYYY-MM-DD): ").strip()
            email = input("Email: ").strip()
            phone = input("Phone: ").strip()
            add_student(fn, ln, dob, email, phone)

        elif choice == "2":
            list_students()

        elif choice == "3":
            kw = input("Search keyword: ").strip()
            search_students(kw)

        elif choice == "4":
            sid = input_int("Student ID to update: ")
            fn = input("New first name: ").strip()
            ln = input("New last name: ").strip()
            dob = input("New DOB (YYYY-MM-DD): ").strip()
            email = input("New email: ").strip()
            phone = input("New phone: ").strip()
            update_student(sid, fn, ln, dob, email, phone)

        elif choice == "5":
            sid = input_int("Student ID to delete: ")
            confirm = input(f"Delete student {sid}? (y/n): ").strip().lower()
            if confirm == "y":
                delete_student(sid)

        elif choice == "6":
            sid = input_int("Student ID: ")
            list_enrollments_by_student(sid)

        elif choice == "0":
            break


def teacher_menu():
    while True:
        print("\n--- Teacher Management ---")
        print("1. Add Teacher")
        print("2. List All Teachers")
        print("3. Update Teacher")
        print("4. Delete Teacher")
        print("0. Back")
        choice = input("Choose: ").strip()

        if choice == "1":
            fn = input("First name: ").strip()
            ln = input("Last name: ").strip()
            email = input("Email: ").strip()
            phone = input("Phone: ").strip()
            spec = input("Subject specialty: ").strip()
            add_teacher(fn, ln, email, phone, spec)

        elif choice == "2":
            list_teachers()

        elif choice == "3":
            tid = input_int("Teacher ID to update: ")
            fn = input("New first name: ").strip()
            ln = input("New last name: ").strip()
            email = input("New email: ").strip()
            phone = input("New phone: ").strip()
            spec = input("New specialty: ").strip()
            update_teacher(tid, fn, ln, email, phone, spec)

        elif choice == "4":
            tid = input_int("Teacher ID to delete: ")
            confirm = input(f"Delete teacher {tid}? (y/n): ").strip().lower()
            if confirm == "y":
                delete_teacher(tid)

        elif choice == "0":
            break


def course_menu():
    while True:
        print("\n--- Course Management ---")
        print("1. Add Course")
        print("2. List All Courses")
        print("3. Update Course")
        print("4. Delete Course")
        print("0. Back")
        choice = input("Choose: ").strip()

        if choice == "1":
            name = input("Course name: ").strip()
            code = input("Course code (e.g. MATH101): ").strip()
            desc = input("Description: ").strip()
            tid = input_int("Teacher ID (or empty for none): ", allow_empty=True)
            cap = input_int("Max capacity (default 30): ", allow_empty=True) or 30
            add_course(name, code, desc, tid, cap)

        elif choice == "2":
            list_courses()

        elif choice == "3":
            cid = input_int("Course ID to update: ")
            name = input("New name: ").strip()
            code = input("New code: ").strip()
            desc = input("New description: ").strip()
            tid = input_int("New teacher ID (or empty): ", allow_empty=True)
            cap = input_int("New max capacity: ", allow_empty=True) or 30
            update_course(cid, name, code, desc, tid, cap)

        elif choice == "4":
            cid = input_int("Course ID to delete: ")
            confirm = input(f"Delete course {cid}? (y/n): ").strip().lower()
            if confirm == "y":
                delete_course(cid)

        elif choice == "0":
            break


def class_menu():
    while True:
        print("\n--- Class Management ---")
        print("1. Add Class")
        print("2. List All Classes")
        print("3. Update Class")
        print("4. Delete Class")
        print("5. Assign Student to Class")
        print("6. Remove Student from Class")
        print("7. View Students in a Class")
        print("0. Back")
        choice = input("Choose: ").strip()

        if choice == "1":
            name = input("Class name (e.g. 6eme A): ").strip()
            level = input("Grade level (e.g. 6eme): ").strip()
            section = input("Section (e.g. A): ").strip()
            year = input("Academic year (e.g. 2025-2026): ").strip()
            tid = input_int("Homeroom teacher ID (or empty): ", allow_empty=True)
            add_class(name, level, section, year, tid)

        elif choice == "2":
            list_classes()

        elif choice == "3":
            cid = input_int("Class ID to update: ")
            name = input("New name: ").strip()
            level = input("New grade level: ").strip()
            section = input("New section: ").strip()
            year = input("New academic year: ").strip()
            tid = input_int("New homeroom teacher ID (or empty): ", allow_empty=True)
            update_class(cid, name, level, section, year, tid)

        elif choice == "4":
            cid = input_int("Class ID to delete: ")
            confirm = input(f"Delete class {cid}? (y/n): ").strip().lower()
            if confirm == "y":
                delete_class(cid)

        elif choice == "5":
            sid = input_int("Student ID: ")
            cid = input_int("Class ID: ")
            assign_student_to_class(sid, cid)

        elif choice == "6":
            sid = input_int("Student ID: ")
            remove_student_from_class(sid)

        elif choice == "7":
            cid = input_int("Class ID: ")
            list_students_in_class(cid)

        elif choice == "0":
            break


def enrollment_menu():
    while True:
        print("\n--- Enrollment & Grades ---")
        print("1. Enroll Student in Course")
        print("2. Unenroll Student from Course")
        print("3. View Students in a Course")
        print("4. Assign / Update Grade")
        print("0. Back")
        choice = input("Choose: ").strip()

        if choice == "1":
            sid = input_int("Student ID: ")
            cid = input_int("Course ID: ")
            enroll_student(sid, cid)

        elif choice == "2":
            sid = input_int("Student ID: ")
            cid = input_int("Course ID: ")
            unenroll_student(sid, cid)

        elif choice == "3":
            cid = input_int("Course ID: ")
            list_enrollments_by_course(cid)

        elif choice == "4":
            eid = input_int("Enrollment ID: ")
            score = input_float("Score (0-100): ")
            remarks = input("Remarks (optional): ").strip()
            assign_grade(eid, score, remarks)

        elif choice == "0":
            break


def parent_menu():
    while True:
        print("\n--- Parent Management ---")
        print("1. Add Parent")
        print("2. List All Parents")
        print("3. Update Parent")
        print("4. Delete Parent")
        print("5. Link Parent to Student")
        print("6. Unlink Parent from Student")
        print("7. View Children of a Parent")
        print("8. View Parents of a Student")
        print("0. Back")
        choice = input("Choose: ").strip()

        if choice == "1":
            fn = input("First name: ").strip()
            ln = input("Last name: ").strip()
            email = input("Email: ").strip()
            phone = input("Phone: ").strip()
            addr = input("Address: ").strip()
            add_parent(fn, ln, email, phone, addr)

        elif choice == "2":
            list_parents()

        elif choice == "3":
            pid = input_int("Parent ID to update: ")
            fn = input("New first name: ").strip()
            ln = input("New last name: ").strip()
            email = input("New email: ").strip()
            phone = input("New phone: ").strip()
            addr = input("New address: ").strip()
            update_parent(pid, fn, ln, email, phone, addr)

        elif choice == "4":
            pid = input_int("Parent ID to delete: ")
            confirm = input(f"Delete parent {pid}? (y/n): ").strip().lower()
            if confirm == "y":
                delete_parent(pid)

        elif choice == "5":
            pid = input_int("Parent ID: ")
            sid = input_int("Student ID: ")
            rel = input("Relationship (Parent/Guardian/Other) [Parent]: ").strip() or "Parent"
            link_parent_to_student(pid, sid, rel)

        elif choice == "6":
            pid = input_int("Parent ID: ")
            sid = input_int("Student ID: ")
            unlink_parent_from_student(pid, sid)

        elif choice == "7":
            pid = input_int("Parent ID: ")
            list_children_of_parent(pid)

        elif choice == "8":
            sid = input_int("Student ID: ")
            list_parents_of_student(sid)

        elif choice == "0":
            break


def attendance_menu():
    while True:
        print("\n--- Attendance Management ---")
        print("1. Mark Single Student Attendance")
        print("2. Mark Attendance for Entire Class")
        print("3. View Attendance by Student")
        print("4. View Attendance by Class & Date")
        print("0. Back")
        choice = input("Choose: ").strip()

        if choice == "1":
            sid = input_int("Student ID: ")
            date = input("Date (YYYY-MM-DD): ").strip()
            print("Status: P=Present, A=Absent, L=Late, E=Excused")
            status_map = {"P": "Present", "A": "Absent", "L": "Late", "E": "Excused"}
            st = input("Status [P/A/L/E]: ").strip().upper()
            status = status_map.get(st)
            if not status:
                print("Invalid status.")
                continue
            remarks = input("Remarks (optional): ").strip()
            mark_attendance(sid, date, status, remarks)

        elif choice == "2":
            cid = input_int("Class ID: ")
            date = input("Date (YYYY-MM-DD): ").strip()
            mark_class_attendance(cid, date)

        elif choice == "3":
            sid = input_int("Student ID: ")
            view_attendance_by_student(sid)

        elif choice == "4":
            cid = input_int("Class ID: ")
            date = input("Date (YYYY-MM-DD): ").strip()
            view_attendance_by_class_date(cid, date)

        elif choice == "0":
            break


def schedule_menu():
    while True:
        print("\n--- Class Scheduling ---")
        print("1. Add Schedule Slot")
        print("2. View Schedule by Class")
        print("3. View Schedule by Student")
        print("4. Delete Schedule Slot")
        print("5. Send Schedule to Student's Parents")
        print("0. Back")
        choice = input("Choose: ").strip()

        if choice == "1":
            cid = input_int("Class ID: ")
            coid = input_int("Course ID: ")
            print("Days: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday")
            day = input("Day of week: ").strip().capitalize()
            start = input("Start time (e.g. 08:00): ").strip()
            end = input("End time (e.g. 09:30): ").strip()
            room = input("Room (optional): ").strip()
            add_schedule_slot(cid, coid, day, start, end, room)

        elif choice == "2":
            cid = input_int("Class ID: ")
            list_schedule_by_class(cid)

        elif choice == "3":
            sid = input_int("Student ID: ")
            view_student_schedule(sid)

        elif choice == "4":
            slot_id = input_int("Schedule slot ID to delete: ")
            delete_schedule_slot(slot_id)

        elif choice == "5":
            sid = input_int("Student ID: ")
            send_schedule_to_parents(sid)

        elif choice == "0":
            break


def main_menu():
    init_db()
    print("=" * 40)
    print("   SCHOOL MANAGEMENT SYSTEM")
    print("=" * 40)

    while True:
        print("\n--- Main Menu ---")
        print("1. Students")
        print("2. Teachers")
        print("3. Courses")
        print("4. Classes")
        print("5. Parents")
        print("6. Enrollments & Grades")
        print("7. Attendance")
        print("8. Scheduling")
        print("0. Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            student_menu()
        elif choice == "2":
            teacher_menu()
        elif choice == "3":
            course_menu()
        elif choice == "4":
            class_menu()
        elif choice == "5":
            parent_menu()
        elif choice == "6":
            enrollment_menu()
        elif choice == "7":
            attendance_menu()
        elif choice == "8":
            schedule_menu()
        elif choice == "0":
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main_menu()
