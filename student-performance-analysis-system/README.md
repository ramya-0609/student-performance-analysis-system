# Student Performance Analysis System

A beginner-friendly Python + Flask + MySQL application for managing student records and marks, calculating performance, and viewing summaries and charts.

## Features
- CRUD for students, subjects, and marks
- Validates marks against each subject's maximum
- Calculates totals, averages, percentage, grade, and pass/fail
- Lists toppers and students below a configurable percentage threshold
- Subject/section summaries and Matplotlib charts
- MySQL persistence

## Stack
Python 3.10+, Flask, MySQL 8+, mysql-connector-python, Pandas, NumPy, Matplotlib.

## 1. Prerequisites
Install Python 3.10 or newer and MySQL Server. During MySQL setup, remember your database username and password. Git is needed for the final push.

## 2. Create environment
### Windows PowerShell
```powershell
cd student-performance-analysis-system
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```
If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again.

Edit `.env` and set your MySQL host, username, password, and database name.

## 3. Create database
Option A: Open MySQL Workbench, connect to your local server, and run:
```sql
CREATE DATABASE IF NOT EXISTS student_performance;
```
Then run the app. It creates the tables automatically.

Option B: from MySQL command line:
```sql
CREATE DATABASE IF NOT EXISTS student_performance;
```

## 4. Start the application
```powershell
python app.py
```
Open http://127.0.0.1:5000 in your browser. Stop with Ctrl+C.

## 5. Suggested first run
1. Add a student (roll number must be unique).
2. Add a subject with max marks and pass marks.
3. Add marks for that student and subject.
4. Open Reports to see grades, pass/fail, and charts.
5. Try invalid marks such as a negative number or a value above max marks; they should be rejected.

## Grade rules
- Percentage >= 90: A+
- >= 80: A
- >= 70: B
- >= 60: C
- >= 50: D
- >= 35: E
- Otherwise: F
Pass/fail is based on each recorded assessment's subject pass mark. The student summary percentage is the average of the percentages across their recorded subject/assessment rows. These are transparent demo rules; adjust them to your institution's official policy before real use.

## 6. Push to GitHub
Create an empty repository on GitHub named `student-performance-analysis-system` (do not add README/license there if this folder already has them). Then run:
```powershell
git init
git add .
git status
git commit -m "Build student performance analysis system"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/student-performance-analysis-system.git
git push -u origin main
```
Replace `YOUR-USERNAME` with your GitHub username. If Git asks you to sign in, complete the browser sign-in prompt. Do not commit `.env` or passwords; `.gitignore` excludes `.env`.

## Troubleshooting
- `Access denied`: check MySQL username/password in `.env` and that MySQL Server is running.
- `Unknown database`: create `student_performance` in MySQL Workbench, then restart the app.
- `ModuleNotFoundError`: activate `.venv` and run `pip install -r requirements.txt`.
- Chart missing: install dependencies again and restart.
