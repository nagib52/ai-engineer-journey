import sqlite3

conn = sqlite3.connect("mydata.db")  # database connection creation
cursor = conn.cursor()

# ===== CREATE TABLE: grade_info =====
cursor.execute("""
CREATE TABLE IF NOT EXISTS grade_info (
    grade TEXT PRIMARY KEY,
    description TEXT
)
""")

cursor.execute("INSERT OR IGNORE INTO grade_info (grade, description) VALUES (?, ?)", ("A", "Excellent"))
cursor.execute("INSERT OR IGNORE INTO grade_info (grade, description) VALUES (?, ?)", ("B", "Good"))
cursor.execute("INSERT OR IGNORE INTO grade_info (grade, description) VALUES (?, ?)", ("C", "Average"))

conn.commit()

# ===== JOIN: students and grade_info =====
cursor.execute("""
SELECT students.name, students.age, grade_info.description
FROM students
JOIN grade_info ON students.grade = grade_info.grade
""")

print("JOIN by students and grade description:")
for row in cursor.fetchall():
    print(row)

conn.close()