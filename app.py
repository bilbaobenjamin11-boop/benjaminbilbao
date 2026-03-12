from flask import Flask, jsonify, request, render_template_string
import sqlite3

app = Flask(__name__)

DATABASE = "students.db"

# Create database and table
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        grade TEXT,
        section TEXT
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
<input id="grade" placeholder="Grade">
<input id="section" placeholder="Section">

<button onclick="addStudent()">Add Student</button>

<table id="studentTable">

<tr>
<th>ID</th>
<th>Name</th>
<th>Grade</th>
<th>Section</th>
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
<th>Grade</th>
<th>Section</th>
<th>Action</th>
</tr>
`

data.forEach(s=>{

table.innerHTML+=`
<tr>
<td>${s.id}</td>
<td>${s.name}</td>
<td>${s.grade}</td>
<td>${s.section}</td>
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
grade:document.getElementById("grade").value,
section:document.getElementById("section").value
})
})

.then(res=>res.json())
.then(data=>{

loadStudents()

document.getElementById("name").value=""
document.getElementById("grade").value=""
document.getElementById("section").value=""

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
            "grade": r[2],
            "section": r[3]
        })

    return jsonify(students)


# Add student
@app.route('/student', methods=['POST'])
def add_student():

    data = request.get_json()

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO students (name,grade,section) VALUES (?,?,?)",
        (data["name"], data["grade"], data["section"])
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
