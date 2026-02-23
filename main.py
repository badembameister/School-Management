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
from enrollments import (
    enroll_student, unenroll_student,
    list_enrollments_by_course, list_enrollments_by_student,
    assign_grade,
)


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
        print("4. Enrollments & Grades")
        print("0. Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            student_menu()
        elif choice == "2":
            teacher_menu()
        elif choice == "3":
            course_menu()
        elif choice == "4":
            enrollment_menu()
        elif choice == "0":
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main_menu()
