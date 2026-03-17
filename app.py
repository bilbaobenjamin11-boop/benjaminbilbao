from flask import Flask, jsonify, request, render_template_string
import sqlite3

app = Flask(__name__)
DATABASE = "students.db"

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
<title>Cyber Student Portal</title>
<style>
    :root {
        --neon-blue: #00d2ff;
        --neon-pink: #ff0055;
        --dark-bg: #0d0d1a;
        --card-bg: #161625;
    }

    body { 
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
        background: var(--dark-bg); 
        color: #fff;
        margin: 0; 
        display: flex;
        justify-content: center;
        min-height: 100vh;
    }

    .container { 
        width: 90%;
        max-width: 900px; 
        margin-top: 50px; 
    }

    .card { 
        background: var(--card-bg); 
        padding: 30px; 
        border-radius: 15px; 
        box-shadow: 0 0 20px rgba(0, 210, 255, 0.2);
        border: 1px solid rgba(0, 210, 255, 0.1);
    }

    h2 { 
        text-align: center; 
        color: var(--neon-blue); 
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 30px;
        text-shadow: 0 0 10px var(--neon-blue);
    }

    .form-grid {
        display: grid;
        grid-template-columns: 2fr 1fr 1fr 1fr;
        gap: 15px;
        margin-bottom: 20px;
    }

    input { 
        padding: 12px; 
        border-radius: 5px; 
        border: 1px solid #333; 
        background: #0a0a12;
        color: white;
        outline: none;
        transition: 0.3s;
    }

    input:focus {
        border-color: var(--neon-blue);
        box-shadow: 0 0 8px var(--neon-blue);
    }

    .btn-container {
        display: flex;
        justify-content: center;
        margin-bottom: 30px;
    }

    button { 
        padding: 12px 30px; 
        background: transparent;
        color: var(--neon-blue); 
        border: 2px solid var(--neon-blue);
        border-radius: 5px; 
        cursor: pointer; 
        font-weight: bold;
        text-transform: uppercase;
        transition: 0.3s;
    }

    button:hover { 
        background: var(--neon-blue);
        color: #000;
        box-shadow: 0 0 15px var(--neon-blue);
    }

    table { 
        width: 100%; 
        border-collapse: collapse; 
        background: rgba(255, 255, 255, 0.02);
    }

    th, td { 
        padding: 15px; 
        text-align: center; 
        border-bottom: 1px solid #333; 
    }

    th { 
        background: rgba(0, 210, 255, 0.1);
        color: var(--neon-blue);
        font-size: 0.9em;
    }

    .status-passed { color: #00ff88; font-weight: bold; }
    .status-failed { color: var(--neon-pink); font-weight: bold; }

    .deleteBtn { border-color: var(--neon-pink); color: var(--neon-pink); padding: 5px 10px; font-size: 0.8em; }
    .deleteBtn:hover { background: var(--neon-pink); color: #fff; box-shadow: 0 0 10px var(--neon-pink); }
    
    .editBtn { border-color: #f1c40f; color: #f1c40f; padding: 5px 10px; font-size: 0.8em; margin-right: 5px; }
    .editBtn:hover { background: #f1c40f; color: #000; box-shadow: 0 0 10px #f1c40f; }
</style>
</head>
<body>

<div class="container">
    <div class="card">
        <h2>Student Management System</h2>

        <input type="hidden" id="studentId">
        
        <div class="form-grid">
            <input id="name" placeholder="Full Name">
            <input id="g1" type="number" placeholder="1st Grade">
            <input id="g2" type="number" placeholder="2nd Grade">
            <input id="g3" type="number" placeholder="3rd Grade">
        </div>

        <div class="btn-container">
            <button id="saveBtn" onclick="saveStudent()">Add Student</button>
        </div>

        <table id="studentTable">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>1st</th>
                    <th>2nd</th>
                    <th>3rd</th>
                    <th>GPA</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="tableBody"></tbody>
        </table>
    </div>
</div>

<script>
function loadStudents(){
    fetch('/students')
    .then(res=>res.json())
    .then(data=>{
        let tbody = document.getElementById("tableBody");
        tbody.innerHTML = "";
        
        data.forEach(s=>{
            let statusClass = s.status === "Passed" ? "status-passed" : "status-failed";
            tbody.innerHTML += `
            <tr>
                <td>${s.id}</td>
                <td>${s.name}</td>
                <td>${s.grade1}</td>
                <td>${s.grade2}</td>
                <td>${s.grade3}</td>
                <td>${s.gpa.toFixed(2)}</td>
                <td class="${statusClass}">${s.status}</td>
                <td>
                    <button class="editBtn" onclick='prepareEdit(${JSON.stringify(s)})'>Edit</button>
                    <button class="deleteBtn" onclick="deleteStudent(${s.id})">Delete</button>
                </td>
            </tr>`
        })
    })
}

function prepareEdit(student){
    document.getElementById("studentId").value = student.id;
    document.getElementById("name").value = student.name;
    document.getElementById("g1").value = student.grade1;
    document.getElementById("g2").value = student.grade2;
    document.getElementById("g3").value = student.grade3;
    document.getElementById("saveBtn").innerText = "Update Record";
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function saveStudent(){
    let id = document.getElementById("studentId").value;
    let url = id ? '/student/' + id : '/student';
    let method = id ? 'PUT' : 'POST';

    const payload = {
        name: document.getElementById("name").value,
        grade1: document.getElementById("g1").value,
        grade2: document.getElementById("g2").value,
        grade3: document.getElementById("g3").value
    };

    if(!payload.name || !payload.grade1) {
        alert("Please fill in the details.");
        return;
    }

    fetch(url, {
        method: method,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    })
    .then(res=>res.json())
    .then(() => {
        loadStudents();
        clearInputs();
    });
}

function clearInputs(){
    document.getElementById("studentId").value = "";
    document.getElementById("name").value = "";
    document.getElementById("g1").value = "";
    document.getElementById("g2").value = "";
    document.getElementById("g3").value = "";
    document.getElementById("saveBtn").innerText = "Add Student";
}

function deleteStudent(id){
    if(confirm("Delete this record?")) {
        fetch('/student/'+id, { method:'DELETE' }).then(() => loadStudents());
    }
}

loadStudents();
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(html_page)

@app.route('/students')
def get_students():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id":r[0],"name":r[1],"grade1":r[2],"grade2":r[3],"grade3":r[4],"gpa":r[5],"status":r[6]} for r in rows])

@app.route('/student', methods=['POST'])
def add_student():
    data = request.get_json()
    g1, g2, g3 = float(data["grade1"]), float(data["grade2"]), float(data["grade3"])
    gpa = (g1 + g2 + g3) / 3
    status = "Passed" if gpa >= 75 else "Failed"
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name,grade1,grade2,grade3,gpa,status) VALUES (?,?,?,?,?,?)",
                   (data["name"], g1, g2, g3, gpa, status))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/student/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json()
    g1, g2, g3 = float(data["grade1"]), float(data["grade2"]), float(data["grade3"])
    gpa = (g1 + g2 + g3) / 3
    status = "Passed" if gpa >= 75 else "Failed"

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""UPDATE students SET name=?, grade1=?, grade2=?, grade3=?, gpa=?, status=? WHERE id=?""",
                   (data["name"], g1, g2, g3, gpa, status, id))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/student/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True)
