from flask import Flask, jsonify, request, render_template_string
import sqlite3

app = Flask(__name__)

DATABASE = "students.db"

# Create database and table with updated columns
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        grade1 REAL,
        grade2 REAL,
        grade3 REAL,
        gpa REAL,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

html_page = """
<!DOCTYPE html>
<html>
<head>
<title>Student Management</title>

<style>

body{
font-family:Arial;
background:linear-gradient(135deg,#4facfe,#00f2fe);
margin:0;
}

.container{
width:800px;
margin:auto;
margin-top:40px;
}

.card{
background:white;
padding:20px;
border-radius:10px;
box-shadow:0 5px 15px rgba(0,0,0,0.2);
}

input{
padding:10px;
margin:5px;
border-radius:5px;
border:1px solid #ccc;
}

button{
padding:10px 15px;
background:#4CAF50;
color:white;
border:none;
border-radius:5px;
cursor:pointer;
}

button:hover{
background:#45a049;
}

table{
width:100%;
border-collapse:collapse;
margin-top:20px;
}

th,td{
border:1px solid #ddd;
padding:10px;
text-align:center;
}

th{
background:#4CAF50;
color:white;
}

.deleteBtn{
background:red;
}

</style>

</head>

<body>

<div class="container">

<div class="card">

<h2>Student Management System</h2>

<input id="name" placeholder="Name">
<input id="g1" type="number" placeholder="Grade 1">
<input id="g2" type="number" placeholder="Grade 2">
<input id="g3" type="number" placeholder="Grade 3">

<button onclick="addStudent()">Add Student</button>

<table id="studentTable">

<tr>
<th>ID</th>
<th>Name</th>
<th>G1</th>
<th>G2</th>
<th>G3</th>
<th>GPA</th>
<th>Status</th>
<th>Action</th>
</tr>

</table>

</div>

</div>

<script>

function loadStudents(){

fetch('/students')
.then(res=>res.json())
.then(data=>{

let table=document.getElementById("studentTable")

table.innerHTML=`
<tr>
<th>ID</th>
<th>Name</th>
<th>G1</th>
<th>G2</th>
<th>G3</th>
<th>GPA</th>
<th>Status</th>
<th>Action</th>
</tr>
`

data.forEach(s=>{

table.innerHTML+=`
<tr>
<td>${s.id}</td>
<td>${s.name}</td>
<td>${s.grade1}</td>
<td>${s.grade2}</td>
<td>${s.grade3}</td>
<td>${s.gpa}</td>
<td>${s.status}</td>
<td>
<button class="deleteBtn" onclick="deleteStudent(${s.id})">Delete</button>
</td>
</tr>
`

})

})

}

function addStudent(){

fetch('/student',{
method:'POST',
headers:{'Content-Type':'application/json'},
body:JSON.stringify({
name:document.getElementById("name").value,
grade1:document.getElementById("g1").value,
grade2:document.getElementById("g2").value,
grade3:document.getElementById("g3").value
})
})

.then(res=>res.json())
.then(data=>{

loadStudents()

document.getElementById("name").value=""
document.getElementById("g1").value=""
document.getElementById("g2").value=""
document.getElementById("g3").value=""

})

}

function deleteStudent(id){

fetch('/student/'+id,{
method:'DELETE'
})
.then(res=>res.json())
.then(data=>{
loadStudents()
})

}

loadStudents()

</script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(html_page)


# Get students
@app.route('/students')
def get_students():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")

    rows = cursor.fetchall()

    conn.close()

    students = []

    for r in rows:
        students.append({
            "id": r[0],
            "name": r[1],
            "grade1": r[2],
            "grade2": r[3],
            "grade3": r[4],
            "gpa": r[5],
            "status": r[6]
        })

    return jsonify(students)


# Add student
@app.route('/student', methods=['POST'])
def add_student():

    data = request.get_json()
    
    # Logic for GPA calculation
    g1 = float(data["grade1"])
    g2 = float(data["grade2"])
    g3 = float(data["grade3"])
    
    gpa = round((g1 + g2 + g3) / 3, 2)
    status = "Passed" if gpa >= 75 else "Failed"

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO students (name,grade1,grade2,grade3,gpa,status) VALUES (?,?,?,?,?,?)",
        (data["name"], g1, g2, g3, gpa, status)
    )

    conn.commit()
    conn.close()

    return jsonify({"message":"Student added"})


# Delete student
@app.route('/student/<int:id>', methods=['DELETE'])
def delete_student(id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return jsonify({"message":"Student deleted"})


if __name__ == '__main__':
    app.run(debug=True)
