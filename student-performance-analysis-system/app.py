from decimal import Decimal, InvalidOperation
from flask import Flask, render_template, request, redirect, url_for, flash
from db import get_connection, initialize_database
from analytics import student_report, chart_as_base64

app = Flask(__name__)
app.secret_key = "local-development-key-change-before-deployment"

def query_all(sql, params=()):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        result = cur.fetchall()
        cur.close()
        return result
    finally:
        conn.close()

def execute(sql, params=()):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        row_id = cur.lastrowid
        cur.close()
        return row_id
    finally:
        conn.close()

def as_decimal(value, label):
    try:
        number = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"{label} must be a valid number.")
    if not number.is_finite():
        raise ValueError(f"{label} must be a finite number.")
    return number

@app.route("/")
def index():
    counts = {
        "students": query_all("SELECT COUNT(*) AS n FROM students")[0]["n"],
        "subjects": query_all("SELECT COUNT(*) AS n FROM subjects")[0]["n"],
        "marks": query_all("SELECT COUNT(*) AS n FROM marks")[0]["n"],
    }
    return render_template("index.html", counts=counts)

@app.route("/students", methods=["GET", "POST"])
def students():
    if request.method == "POST":
        roll_no = request.form.get("roll_no", "").strip()
        name = request.form.get("name", "").strip()
        section = request.form.get("section", "").strip()
        if not all([roll_no, name, section]):
            flash("Please fill in every student field.", "error")
        else:
            try:
                execute("INSERT INTO students (roll_no, name, section) VALUES (%s,%s,%s)", (roll_no, name, section))
                flash("Student added.", "success")
                return redirect(url_for("students"))
            except Exception as exc:
                flash(f"Could not add student. Check that the roll number is unique. Details: {exc}", "error")
    return render_template("students.html", students=query_all("SELECT * FROM students ORDER BY section, roll_no"))

@app.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
def edit_student(student_id):
    found = query_all("SELECT * FROM students WHERE student_id=%s", (student_id,))
    if not found:
        flash("Student not found.", "error")
        return redirect(url_for("students"))
    student = found[0]
    if request.method == "POST":
        values = tuple(request.form.get(key, "").strip() for key in ("roll_no", "name", "section"))
        if not all(values):
            flash("Please fill in every field.", "error")
        else:
            try:
                execute("UPDATE students SET roll_no=%s, name=%s, section=%s WHERE student_id=%s", (*values, student_id))
                flash("Student updated.", "success")
                return redirect(url_for("students"))
            except Exception as exc:
                flash(f"Could not update student: {exc}", "error")
    return render_template("edit_student.html", student=student)

@app.post("/students/<int:student_id>/delete")
def delete_student(student_id):
    execute("DELETE FROM students WHERE student_id=%s", (student_id,))
    flash("Student deleted. Their marks were deleted too.", "success")
    return redirect(url_for("students"))

@app.route("/subjects", methods=["GET", "POST"])
def subjects():
    if request.method == "POST":
        name = request.form.get("subject_name", "").strip()
        try:
            maximum = as_decimal(request.form.get("max_marks"), "Maximum marks")
            passing = as_decimal(request.form.get("pass_marks"), "Pass marks")
            if not name:
                raise ValueError("Subject name is required.")
            if maximum <= 0 or passing < 0 or passing > maximum:
                raise ValueError("Require max marks > 0 and pass marks between 0 and max marks.")
            execute("INSERT INTO subjects (subject_name, max_marks, pass_marks) VALUES (%s,%s,%s)", (name, maximum, passing))
            flash("Subject added.", "success")
            return redirect(url_for("subjects"))
        except ValueError as exc:
            flash(str(exc), "error")
        except Exception as exc:
            flash(f"Could not add subject (subject names must be unique): {exc}", "error")
    return render_template("subjects.html", subjects=query_all("SELECT * FROM subjects ORDER BY subject_name"))

@app.post("/subjects/<int:subject_id>/delete")
def delete_subject(subject_id):
    execute("DELETE FROM subjects WHERE subject_id=%s", (subject_id,))
    flash("Subject deleted. Its marks were deleted too.", "success")
    return redirect(url_for("subjects"))

@app.route("/marks", methods=["GET", "POST"])
def marks():
    students_list = query_all("SELECT student_id, roll_no, name, section FROM students ORDER BY roll_no")
    subjects_list = query_all("SELECT * FROM subjects ORDER BY subject_name")
    if request.method == "POST":
        try:
            student_id = int(request.form.get("student_id", ""))
            subject_id = int(request.form.get("subject_id", ""))
            assessment = request.form.get("assessment", "Internal").strip() or "Internal"
            value = as_decimal(request.form.get("marks_obtained"), "Marks")
            subject_rows = query_all("SELECT * FROM subjects WHERE subject_id=%s", (subject_id,))
            if not query_all("SELECT student_id FROM students WHERE student_id=%s", (student_id,)):
                raise ValueError("Choose a valid student.")
            if not subject_rows:
                raise ValueError("Choose a valid subject.")
            subject = subject_rows[0]
            if value < 0 or value > Decimal(str(subject["max_marks"])):
                raise ValueError(f"Marks must be between 0 and {subject['max_marks']}.")
            execute("""INSERT INTO marks (student_id, subject_id, assessment, marks_obtained)
                       VALUES (%s,%s,%s,%s)
                       ON DUPLICATE KEY UPDATE marks_obtained=VALUES(marks_obtained)""",
                    (student_id, subject_id, assessment, value))
            flash("Marks saved. Existing student/subject/assessment marks are updated.", "success")
            return redirect(url_for("marks"))
        except (ValueError, InvalidOperation) as exc:
            flash(str(exc), "error")
        except Exception as exc:
            flash(f"Could not save marks: {exc}", "error")
    rows = query_all("""SELECT m.mark_id, s.roll_no, s.name, s.section, sub.subject_name,
                        m.assessment, m.marks_obtained, sub.max_marks, sub.pass_marks
                        FROM marks m JOIN students s ON s.student_id=m.student_id
                        JOIN subjects sub ON sub.subject_id=m.subject_id
                        ORDER BY s.section, s.roll_no, sub.subject_name, m.assessment""")
    return render_template("marks.html", students=students_list, subjects=subjects_list, marks=rows)

@app.post("/marks/<int:mark_id>/delete")
def delete_mark(mark_id):
    execute("DELETE FROM marks WHERE mark_id=%s", (mark_id,))
    flash("Marks record deleted.", "success")
    return redirect(url_for("marks"))

@app.route("/reports")
def reports():
    threshold_raw = request.args.get("threshold", "50")
    try:
        threshold = float(threshold_raw)
        if not 0 <= threshold <= 100:
            threshold = 50
    except ValueError:
        threshold = 50
    rows = query_all("""SELECT s.student_id, s.roll_no, s.name, s.section,
                        sub.subject_name, CAST(sub.max_marks AS DOUBLE) AS max_marks,
                        CAST(sub.pass_marks AS DOUBLE) AS pass_marks,
                        CAST(m.marks_obtained AS DOUBLE) AS marks_obtained,
                        m.assessment
                        FROM marks m JOIN students s ON s.student_id=m.student_id
                        JOIN subjects sub ON sub.subject_id=m.subject_id""")
    reports_data, details, stats = student_report(rows, threshold)
    subject_stats = query_all("""SELECT sub.subject_name,
                        AVG(m.marks_obtained / sub.max_marks * 100) AS average_percentage,
                        AVG(CASE WHEN m.marks_obtained >= sub.pass_marks THEN 100 ELSE 0 END) AS pass_percentage,
                        COUNT(*) AS records_count
                        FROM marks m JOIN subjects sub ON sub.subject_id=m.subject_id
                        GROUP BY sub.subject_id, sub.subject_name ORDER BY sub.subject_name""")
    section_stats = query_all("""SELECT s.section, COUNT(DISTINCT s.student_id) AS students_count,
                        AVG(m.marks_obtained / sub.max_marks * 100) AS average_percentage
                        FROM students s LEFT JOIN marks m ON m.student_id=s.student_id
                        LEFT JOIN subjects sub ON sub.subject_id=m.subject_id
                        GROUP BY s.section ORDER BY s.section""")
    avg_chart = chart_as_base64(
        [r["subject_name"] for r in subject_stats],
        [float(r["average_percentage"] or 0) for r in subject_stats],
        "Subject-wise Average Percentage", "Average (%)")
    pass_chart = chart_as_base64(
        [r["subject_name"] for r in subject_stats],
        [float(r["pass_percentage"] or 0) for r in subject_stats],
        "Subject-wise Pass Percentage", "Pass (%)")
    return render_template("reports.html", reports=reports_data, subjects=subject_stats,
                           sections=section_stats, stats=stats, threshold=threshold,
                           avg_chart=avg_chart, pass_chart=pass_chart)

if __name__ == "__main__":
    initialize_database()
    app.run(debug=True, host="127.0.0.1", port=5000)
