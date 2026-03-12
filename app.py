from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

students = [
    {"id": 1, "name": "BNJ", "grade": 3, "section": "BSIT-2 ARDUINO"}
]

html_page = """
<!DOCTYPE html>
<html>
<head>
<title>Student Management System</title>

<style>

body{
    font-family: Arial;
    background: linear-gradient(135deg,#4facfe,#00f2fe);
    margin:0;
    padding:0;
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

h1{
    text-align:center;
}

input{
    padding:10px;
    margin:5px;
    border-radius:5px;
    border:1px solid #ccc;
}

button{
    padding:10px 15px;
    border:none;
    background:#4CAF50;
    color:white;
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

tr:hover{
    background:#f5f5f5;
}

.deleteBtn{
    background:red;
}

.deleteBtn:hover{
    background:darkred;
}

</style>
</head>

<body>

<div class="container">

<div class="card">

<h1>Student Management</h1>

<h3>Add Student</h3>

<input id="name" placeholder="Name">
<input id="grade" placeholder="Grade">
<input id="section" placeholder="Section">

<button onclick="addStudent()">Add Student</button>

<h3>Student List</h3>

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

let table = document.getElementById("studentTable");

table.innerHTML = `
<tr>
<th>ID</th>
<th>Name</th>
<th>Grade</th>
<th>Section</th>
<th>Action</th>
</tr>
`;

data.forEach(s => {

table.innerHTML += `
<tr>
<td>${s.id}</td>
<td>${s.name}</td>
<td>${s.grade}</td>
<td>${s.section}</td>
<td>
<button class="deleteBtn" onclick="deleteStudent(${s.id})">Delete</button>
</td>
</tr>
`;

});

});

}

function addStudent(){

let name = document.getElementById("name").value
let grade = document.getElementById("grade").value
let section = document.getElementById("section").value

fetch('/student',{
method:'POST',
headers:{'Content-Type':'application/json'},
body: JSON.stringify({
name:name,
grade:grade,
section:section
})
})

.then(res=>res.json())
.then(data=>{

loadStudents()

// Clear form automatically
document.getElementById("name").value=""
document.getElementById("grade").value=""
document.getElementById("section").value=""

document.getElementById("name").focus()

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

@app.route('/students', methods=['GET'])
def get_students():
    return jsonify(students)

@app.route('/student', methods=['POST'])
def add_student():
    data = request.get_json()

    new_student = {
        "id": len(students) + 1,
        "name": data["name"],
        "grade": data["grade"],
        "section": data["section"]
    }

    students.append(new_student)

    return jsonify({"message":"Student added"})

@app.route('/student/<int:id>', methods=['DELETE'])
def delete_student(id):

    for student in students:
        if student["id"] == id:
            students.remove(student)
            return jsonify({"message":"Deleted"})

    return jsonify({"error":"Student not found"})

if __name__ == '__main__':
    app.run(debug=True)
