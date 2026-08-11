import sqlite3

# database connection creation
conn = sqlite3.connect("mydata.db")
cursor = conn.cursor()

# ===== create table =====
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER,
    grade TEXT
)
""")

# ===== insert data =====
cursor.execute("INSERT INTO students (name, age, grade) VALUES (?, ?, ?)", ("Rahim", 20, "A"))
cursor.execute("INSERT INTO students (name, age, grade) VALUES (?, ?, ?)", ("Karim", 22, "B"))
cursor.execute("INSERT INTO students (name, age, grade) VALUES (?, ?, ?)", ("Salma", 19, "A"))
cursor.execute("INSERT INTO students (name, age, grade) VALUES (?, ?, ?)", ("Nadia", 25, "C"))

conn.commit()  # commit the changes to the database

# ===== view all data =====
cursor.execute("SELECT * FROM students")
print("All students:")
for row in cursor.fetchall():
    print(row)

# ===== WHERE clause for filtering =====
cursor.execute("SELECT * FROM students WHERE age > 20")
print("\nStudents older than 20:")
for row in cursor.fetchall():
    print(row)

# ===== GROUP BY for aggregation =====
cursor.execute("SELECT grade, COUNT(*) FROM students GROUP BY grade")
print("\nNumber of students by grade:")
for row in cursor.fetchall():
    print(row)

conn.close()


