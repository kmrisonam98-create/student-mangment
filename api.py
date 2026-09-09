
from fastapi import FastAPI, HTTPException
import sqlite3
import uvicorn
from models import student_register_model
from models import student_login_model
from models import admin_login_model
from models import attendance_model 
from models import result_model

app = FastAPI(title="Student API")


conn = sqlite3.connect(
    "student_database.db",
    check_same_thread=False
)

cursor = conn.cursor()



cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    grade TEXT,
    email TEXT
)
""")

conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    date TEXT,
    status TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id)
)
               
""")

conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS results(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    subject TEXT,
    marks INTEGER,
    total_marks INTEGER,
    FOREIGN KEY(student_id) REFERENCES students(id)
)               
""")
conn.commit()




@app.post("/add_student")
def add_student(model: student_register_model):

    cursor.execute(
        """
        INSERT INTO students (name, age, grade, email, password)
        VALUES (?, ?, ?, ?, ?)
        """,
        (model.name, model.age, model.grade, model.email,model.password)
    )

    conn.commit()

    return {
        "message": "Student added successfully"
    }



@app.get("/students")
def get_students():

    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()

    students = []

    for row in rows:
        students.append({
            "id": row[0],
            "name": row[1],
            "age": row[2],
            "grade": row[3],
            "email": row[4]
        })

    return students



@app.get("/students/{student_id}")
def get_student(student_id: int):

    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    )

    row = cursor.fetchone()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return {
        "id": row[0],
        "name": row[1],
        "age": row[2],
        "grade": row[3],
        "email": row[4]
    }

@app.put("/students/{student_id}")
def update_student(student_id: int, model: student_register_model):

    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    )

    row = cursor.fetchone()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    cursor.execute(
        """
        UPDATE students
        SET name = ?, age = ?, grade = ?, email = ?
        WHERE id = ?
        """,
        (
            model.name,
            model.age,
            model.grade,
            model.email,
            student_id
        )
    )

    conn.commit()

    return {
        "message": "Student updated successfully"
    }
    

@app.delete("/students{student_id}")
def delete_student(student_id: int):
    
    cursor.execute(
        "SELECT  * FROM students WHERE id = ?",
        (student_id,)
    )
    row = cursor.fetchone()
    if not row:
        raise HTTPException(
            status_code=404,
            detail="student not found"
        )
    cursor.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )
    conn.commit()
    return {
        "message": "Student deleted successfully"
    }    



@app.get("/search_student")
def search_student(name: str):
    cursor.execute(
        "SELECT * FROM students WHERE name LIKE ?",
        (f"%{name}%",)
    )
    rows = cursor.fetchall()
    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )
    students = []
    
    for row in rows:
        students.append({
            "id": row[0],
            "name": row[1],
            "age": row[2],
            "grade": row[3],
            "email": row[4],
        })
    return students 



@app.get("/students/grade/{grade}")
def filter_by_grade(grade: str):
    cursor.execute(
        "SELECT * FROM students WHERE grade = ?",
        (grade,)
    )
    rows = cursor.fetchall()
    
    if not rows:
        raise HTTPException(
            status_code=404,
            detail="No students found for this grade"
        )
    
    students = []
    for row in rows:
        students.append({
            "id": row[0],
            "name": row[1],
            "age": row[2],
            "grade": row[3],
            "email": row[4]
        })
        
    return students 

@app.post("/student_login")
def student_login(model: student_login_model):   
    
    cursor.execute(
        """
        SELECT * FROM students
        WHERE email = ? AND password = ?
        
        """,
        (model.email, model.password)
    )
    
    student = cursor.fetchone()
    
    if not student:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    return {
        "message": "Login successful",
        "student_id":student[0],
        "name": student[1],
        "email": student[4]
    }    
    
@app.post("/admin_login")
def admin_login(model: admin_login_model):    
    admin_email = "admin@gmail.com"
    admin_password = "admin123"
    
    if model.email != admin_email or model.password != admin_password:
        raise HTTPException(
            status_code=401,
            detail="Invalid admin email or password"
        )
    return {
        "message": "Admin login successful",
        "role": "admin"
    } 
    
    
    
@app.post("/attendance")
def mark_attendance(model: attendance_model):
    
    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (model.student_id,)
    )
    
    student = cursor.fetchone()
    
    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )
        
    cursor.execute(
        """
        INSERT INTO attendance (student_id, date, status)
        VALUES (?, ?, ?)
        """,
        (
            model.student_id,
            model.date,
            model.status
        )
    ) 
    
    conn.commit()
    
    return {
        "message": "Attendance marked successfully"
    }          
    

@app.get("/attendance/{student_id}")
def get_attendance(student_id: int):
    cursor.execute(
        """
        SELECT * FROM attendance
        WHERE student_id = ?
        """,
        (student_id,)
    ) 
    
    rows = cursor.fetchall()
    if not rows:
        raise HTTPException(
            status_code=404,
            detail = "Attendance not found"
        )
        
    attendance = []
    for row in rows:
        attendance.append({
            "id": row[0],
            "student_id": row[1],
            "date": row[2],
            "status": row[3]
        })    
    return attendance 


@app.post("/results")
def add_result(model: result_model):
    
    
    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (model.student_id,)
    )
    
    student = cursor.fetchone()
    
    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )  
        
    
    if model.marks < 0:
        raise HTTPException(
            status_code=400,
            detail="Marks cannot be negative"
        )    
        
    if model.marks > model.total_marks:
        raise HTTPException(
            status_code=400,
            detail="Marks cannot be greater than total marks"
        )  
    
    
    cursor.execute(
        """
        INSERT INTO results
        (student_id, subject, marks, total_marks)
        VALUES (?, ?, ?, ?)
        """,
        (
            model.student_id,
            model.subject,
            model.marks,
            model.total_marks
        )
    ) 
    
    conn.commit()
    return {
        "message": "Results added successfully"
    }   
        
@app.get("/results/{student_id}")
def get_results(student_id: int):
    cursor.execute(
        """
        SELECT * FROM results
        WHERE student_id = ?
        """,
        (student_id,)
    )
    
    rows = cursor.fetchall()
    
    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Result not found"
        )
    results = []
    
    for row in rows:
        percentage = (row[3] / row[4]) *100
        
        if percentage >= 90:
            grade = "A+"
        elif percentage >= 80:
            grade = "A"
        elif percentage >= 70:
            grade = "B"
        elif percentage >= 60:
            grade = "c"
        elif percentage >= 50:
            grade = "D"
        else:
            grade = "F"
            
        results.append({
            "id": row[0],
            "student_id": row[1],
            "subject": row[2],
            "marks": row[3],
            "total_marks": row[4],
            "percentage": percentage,
            "grade": grade
        })                                   
        

@app.get("/attendance_percentage/{student_id}")
def attendance_percentage(student_id: int):
    
    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    )
    
    student = cursor.fetchone()
    
    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )
        
    
    cursor.execute(
        """
        SELECT status FROM attendance
        WHERE student_id = ?
        """,
        (student_id,)
    ) 
    rows = cursor.fetchall()
    
    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Attendance not found"
        )
    total_classes = len(rows)
    present_classes = 0
    
    for row in rows:
        if row[0].lower() == "present":
            present_classes +=1
            
    percentage = (present_classes / total_classes) * 100
    
    return {
        "student_id": student_id,
        "total_classes": total_classes,
        "present": present_classes,
        "absent": total_classes - present_classes,
        "attendance_percentage": round(percentage, 2)
    }               
    

@app.get("/overall_result/{student_id}")
def overall_result(student_id: int):
    
    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    )    
    student = cursor.fetchone()
    
    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )
    
    
    cursor.execute(
        """
        SELECT subjects, marks, total_marks
        FROM results
        WHERE student_id = ?
        """,
        (student_id,)
        
    )    
    rows = cursor.fetchall()
    
    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Result not found"
        )
    
    
    total_marks_obtained = 0
    total_marks = 0
    
    subjects = []
    
    for row in rows:
        subject = row[0]
        marks = row[1]
        maximum_marks = row[2]
        
        total_marks_obtained +=marks
        total_marks += maximum_marks
        
        subjects.append({
            "subject": subject,
            "marks": marks,
            "total_marks": maximum_marks
        })
    
    percentage = (total_marks_obtained / total_marks) * 100
    
    if percentage >= 90:
        grade = "A+"
    elif percentage >= 80:
        grade = "A"
    elif percentage >= 70:
        grade = "B"
    elif percentage >= 60:
        grade = "C"
    elif percentage >= 50:
        grade = "D"
    else:
        grade = "F"
    
    
    return {
        "stuent_id": student_id,
        "subjects": subjects,
        "total_mark_obtained": total_marks_obtained,
        "total_marks": total_marks,
        "overall_percentage": round(percentage, 2),
        "overall_grade": grade
    }                        


        
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

