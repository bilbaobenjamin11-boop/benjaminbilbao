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
<title>Cyber Student Management</title>
<style>
    :root {
        --neon-pink: #ff007f;
        --neon-blue: #00f2ff;
        --bg-dark: #050505;
        --card-bg: rgba(20, 20, 20, 0.95);
    }

    body { 
        font-family: 'Courier New', Courier, monospace; 
        background-color: var(--bg-dark);
        background-image: 
            linear-gradient(rgba(255, 0, 127, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 0, 127, 0.05) 1px, transparent 1px);
        background-size: 30px 30px;
        color: #fff;
        margin: 0;
        display: flex;
        justify-content: center;
        padding: 40px 20px;
    }

    .container { width: 100%; max-width: 900px; }

    .card { 
        background: var(--card-bg); 
        padding: 30px; 
        border-radius: 5px; 
        border: 2px solid var(--neon-pink);
        box-shadow: 0 0 20px rgba(255, 0, 127, 0.3), inset 0 0 10px rgba(255, 0, 127, 0.2);
    }

    h2 { 
        text-align: center; 
        color: var(--neon-pink); 
        text-transform: uppercase;
        letter-spacing: 5px;
        text-shadow: 0 0 10px var(--neon-pink);
        margin-top: 0;
    }

    .form-row {
        display: grid;
        grid-template-columns: 2fr 1fr 1fr 1fr;
        gap: 10px;
        margin-bottom: 20px;
    }

    input { 
        background: #000;
        border: 1px solid var(--neon-pink);
        padding: 12px; 
        color: var(--neon-blue);
        border-radius: 0;
        outline: none;
    }

    input:focus {
        box-shadow: 0 0 10px var(--neon-blue);
        border-color: var(--neon-blue);
    }

    .action-bar {
        text-align: center;
        margin-bottom: 30px;
    }

    button { 
        padding: 12px 25px; 
        background: transparent;
        color: var(--neon-pink); 
        border: 2px solid var(--neon-pink);
        cursor: pointer; 
        font-weight: bold;
        text-transform: uppercase;
        transition: 0.3s;
    }

    button:hover { 
        background: var(--neon-pink);
        color: #000;
        box-shadow: 0 0 20px var(--neon-pink);
    }

    table { 
        width: 100%; 
        border-collapse: collapse; 
        margin-top: 20px;
    }

    th { 
        border-bottom: 2px solid var(--neon-blue);
        color: var(--neon-blue);
        padding: 15px;
        text-transform: uppercase;
        font-size: 0.85em;
    }

    td { 
        padding: 15px; 
        text-align: center; 
        border-bottom: 1px solid #222;
        font-size: 0.9em;
    }

    .status-passed { color: var(--neon-blue); text-shadow: 0 0 5px var(--neon-blue); }
    .status-failed { color: var(--neon-pink); text-shadow: 0 0 5px var(--neon-pink); }

    .editBtn { border-color: #f1c40f; color: #f1c40f; padding: 5px 10px; margin-right: 5px; }
    .editBtn:hover { background: #f1c40f; color: #000; }

    .deleteBtn { border-color: #ff4b2b; color: #ff4b2b; padding: 5px 10px; }
    .deleteBtn:hover { background: #ff4b2b; color: #000; }

</style>
</head>
<body>

<div class="container">
    <div class="card">
        <h2>System Terminal</h2>

        <input type="hidden" id="studentId">
        
        <div class="form-row">
            <input id="name" placeholder="IDENT_NAME">
            <input id="g1" type="number" placeholder="1ST_GRD">
            <input id="g2" type="number" placeholder="2ND_GRD">
            <input id="g3" type="number" placeholder="3RD_GRD">
        </div>

        <div class="action-bar">
            <button id="saveBtn" onclick="saveStudent()">Execute Entry</button>
        </div>

        <table id="studentTable">
            <thead>
                <tr>
                    <th>UID</th>
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
                <td>#${s.id}</td>
                <td>${s.name}</td>
                <td>${s.grade1}</td>
                <td>${s.grade2}</td>
                <td>${s.grade3}</td>
                <td>${s.gpa.toFixed(2)}</td>
                <td class="${statusClass}">${s.status.toUpperCase()}</td>
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
    document.getElementById("saveBtn").innerText = "Update Entry";
}

function saveStudent(){
    let id = document.getElementById("studentId").value;
    let url = id ? '/student/' + id : '/student';
    let method = id ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            name: document.getElementById("name").value,
            grade1: document.getElementById("g1").value,
            grade2: document.getElementById("g2").value,
            grade3: document.getElementById("g3").value
        })
    })
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
    document.getElementById("saveBtn").innerText = "Execute Entry";
}

function deleteStudent(id){
    fetch('/student/'+id, { method:'DELETE' }).then(() => loadStudents());
}

loadStudents();
</script>
</body>
</html>
"""

# ... [Flask Routes remain identical to previous working update code] ...

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
    cursor.execute("INSERT INTO students (name,grade1,grade2,grade3,gpa,status) VALUES (?,?,?,?,?,?)", (data["name"], g1, g2, g3, gpa, status))
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
    cursor.execute("UPDATE students SET name=?, grade1=?, grade2=?, grade3=?, gpa=?, status=? WHERE id=?", (data["name"], g1, g2, g3, gpa, status, id))
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
