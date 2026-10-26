
from db import get_connection

conn = get_connection()
cursor = conn.cursor()

try:
    # Add sample students
    students = [
        ("101", "Ananya", "A"),
        ("102", "Rahul", "A"),
        ("103", "Priya", "B"),
        ("104", "Arjun", "B"),
        ("105", "Kavya", "A"),
        ("106", "Sneha", "A"),
        ("107", "Vikram", "B"),
        ("108", "Divya", "A"),
        ("109", "Sai Kiran", "B"),
        ("110", "Meghana", "A"),
        ("111", "Rohit", "B"),
        ("112", "Sravya", "A"),
        ("113", "Nikhil", "B"),
        ("114", "Harika", "A"),
        ("115", "Aditya", "B"),
    ]

    cursor.executemany(
        """
        INSERT INTO students (roll_no, name, section)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE name = VALUES(name), section = VALUES(section)
        """,
        students,
    )

    # Add sample subjects
    subjects = [
        ("python", 100, 40),
        ("Database Systems", 100, 40),
        ("Mathematics", 100, 40),
    ]

    cursor.executemany(
        """
        INSERT INTO subjects (subject_name, max_marks, pass_marks)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
        max_marks = VALUES(max_marks),
        pass_marks = VALUES(pass_marks)
        """,
        subjects,
    )
    cursor.execute("SELECT roll_no, student_id FROM students")
    student_ids = dict(cursor.fetchall())

    cursor.execute("SELECT subject_name, subject_id FROM subjects")
    subject_ids = dict(cursor.fetchall())

      # Add sample assessment marks
    marks = [
        ("101", "python", 85),
        ("101", "Database Systems", 78),
        ("101", "Mathematics", 90),
        ("102", "python", 65),
        ("102", "Database Systems", 72),
        ("102", "Mathematics", 58),
        ("103", "python", 92),
        ("103", "Database Systems", 88),
        ("103", "Mathematics", 95),
        ("104", "python", 35),
        ("104", "Database Systems", 55),
        ("104", "Mathematics", 42),
        ("105", "python", 76),
        ("105", "Database Systems", 81),
        ("105", "Mathematics", 69),
    ]

    for roll_no, subject_name, score in marks:
        cursor.execute(
            """
            INSERT INTO marks
                (student_id, subject_id, assessment, marks_obtained)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE marks_obtained = VALUES(marks_obtained)
            """,
            (
                student_ids[roll_no],
                subject_ids[subject_name],
                "Internal",
                score,
            ),
        )

    conn.commit()
    print("Sample students, subjects, and marks added successfully!")

except Exception as error:
    conn.rollback()
    print("Error:", error)

finally:
    cursor.close()
    conn.close()
