
from db import get_connection

conn = get_connection()
cursor = conn.cursor()

try:
    marks = [
        ("106", "python", 88),
        ("106", "Database Systems", 79),
        ("106", "Mathematics", 91),

        ("107", "python", 67),
        ("107", "Database Systems", 74),
        ("107", "Mathematics", 62),

        ("108", "python", 95),
        ("108", "Database Systems", 89),
        ("108", "Mathematics", 93),

        ("109", "python", 72),
        ("109", "Database Systems", 68),
        ("109", "Mathematics", 75),

        ("110", "python", 84),
        ("110", "Database Systems", 92),
        ("110", "Mathematics", 86),

        ("111", "python", 45),
        ("111", "Database Systems", 58),
        ("111", "Mathematics", 49),

        ("112", "python", 91),
        ("112", "Database Systems", 85),
        ("112", "Mathematics", 88),

        ("113", "python", 63),
        ("113", "Database Systems", 71),
        ("113", "Mathematics", 66),

        ("114", "python", 78),
        ("114", "Database Systems", 82),
        ("114", "Mathematics", 73),

        ("115", "python", 87),
        ("115", "Database Systems", 76),
        ("115", "Mathematics", 80),
    ]

    cursor.execute("SELECT roll_no, student_id FROM students")
    student_ids = dict(cursor.fetchall())

    cursor.execute("SELECT subject_name, subject_id FROM subjects")
    subject_ids = {
        name.lower(): subject_id
        for name, subject_id in cursor.fetchall()
    }

    for roll_no, subject_name, score in marks:
        if roll_no not in student_ids:
            print(f"Student {roll_no} not found; skipping.")
            continue

        subject_key = subject_name.lower()
        if subject_key not in subject_ids:
            print(f"Subject {subject_name} not found; skipping.")
            continue

        cursor.execute(
            """
            INSERT INTO marks
                (student_id, subject_id, assessment, marks_obtained)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                marks_obtained = VALUES(marks_obtained)
            """,
            (
                student_ids[roll_no],
                subject_ids[subject_key],
                "Internal",
                score,
            ),
        )

    conn.commit()
    print("Marks added successfully for the new students!")

except Exception as error:
    conn.rollback()
    print("Error:", error)

finally:
    cursor.close()
    conn.close()
