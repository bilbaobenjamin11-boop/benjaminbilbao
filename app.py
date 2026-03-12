from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

# Sample database
students = [
    {"id": 1, "name": "BNJ", "grade": 3, "section": "BSIT-2 ARDUINO"}
]

# Simple HTML Interface
html_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Student API Interface</title>
    <style>
        body { font-family: Arial; margin: 40px; }
        input { padding:5px; margin:5px; }
        button { padding:5px 10px; }
        table { border-collapse: collapse; margin-top:20px;}
        th, td { border:1px solid #ccc; padding:8px;}
    </style>
</head>
<body>

<h1>Student Management</h1>

<h3>Add Student</h3>
<input id="name" placeholder="Name">
<input id="grade" placeholder="Grade">
<input id="section" placeholder="Section">
<button onclick="addStudent()">Add</button>

<h3>Student List</h3>
<table id="studentTable">
<tr>
<th>ID</th>
<th>Name</th>
<th>Grade</th>
<th>Section</th>
</tr>
</table>

<script>

function loadStudents(){
    fetch('/students')
    .then(res => res.json())
    .then(data => {
        let table = document.getElementById("studentTable");
        table.innerHTML = "<tr><th>ID</th><th>Name</th><th>Grade</th><th>Section</th></tr>";

        data.forEach(s => {
            table.innerHTML += `
            <tr>
            <td>${s.id}</td>
            <td>${s.name}</td>
            <td>${s.grade}</td>
            <td>${s.section}</td>
            </tr>`;
        });
    });
}

function addStudent(){
    fetch('/student', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({
            name: document.getElementById("name").value,
            grade: document.getElementById("grade").value,
            section: document.getElementById("section").value
        })
    })
    .then(res=>res.json())
    .then(data=>{
        alert(data.message);
        loadStudents();
    });
}

loadStudents();

</script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(html_page)

# Get all students
@app.route('/students', methods=['GET'])
def get_students():
    return jsonify(students)

# Get single student
@app.route('/student/<int:id>', methods=['GET'])
def get_student(id):
    for student in students:
        if student["id"] == id:
            return jsonify(student)
    return jsonify({"error": "Student not found"}), 404

# Add student
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

    return jsonify({"message": "Student added successfully", "student": new_student})

# Delete student
@app.route('/student/<int:id>', methods=['DELETE'])
def delete_student(id):
    for student in students:
        if student["id"] == id:
            students.remove(student)
            return jsonify({"message": "Student deleted"})
    return jsonify({"error": "Student not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
