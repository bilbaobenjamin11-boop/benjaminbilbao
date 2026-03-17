from flask import Flask, jsonify, request, render_template_string
import sqlite3

app = Flask(__name__)
DATABASE = "students.db"

ADMIN_USER = "admin"
ADMIN_PASS = "cyber123"

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Removed subject, added student_type
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        student_type TEXT,
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
<title>Cyber Grade System</title>
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
        background-image: linear-gradient(rgba(255, 0, 127, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 0, 127, 0.05) 1px, transparent 1px);
        background-size: 30px 30px; color: #fff; margin: 0; display: flex; flex-direction: column; align-items: center; padding: 40px 20px;
    }

    .container { width: 100%; max-width: 1000px; }
    .card { background: var(--card-bg); padding: 30px; border: 2px solid var(--neon-pink); box-shadow: 0 0 20px rgba(255, 0, 127, 0.3); }
    h2 { text-align: center; color: var(--neon-pink); letter-spacing: 5px; text-shadow: 0 0 10px var(--neon-pink); }

    .form-grid { display: grid; grid-template-columns: 2fr 1.5fr 1fr 1fr 1fr; gap: 10px; margin-bottom: 20px; }
    input, select { background: #000; border: 1px solid var(--neon-pink); padding: 12px; color: var(--neon-blue); outline: none; }
    
    button { padding: 10px 20px; background: transparent; color: var(--neon-pink); border: 2px solid var(--neon-pink); cursor: pointer; font-weight: bold; text-transform: uppercase; transition: 0.3s; }
    button:hover { background: var(--neon-pink); color: #000; box-shadow: 0 0 15px var(--neon-pink); }

    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th { border-bottom: 2px solid var(--neon-blue); color: var(--neon-blue); padding: 15px; }
    td { padding: 15px; text-align: center; border-bottom: 1px solid #222; }

    .modal { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); display: none; justify-content: center; align-items: center; z-index: 2000; }
    .modal-content { background: #111; padding: 30px; border: 2px solid var(--neon-blue); width: 500px; }

    #adminPortal { display: none; }
    .nav-bar { width: 100%; max-width: 1000px; display: flex; justify-content: flex-end; margin-bottom: 10px; }
    .status-passed { color: var(--neon-blue); }
    .status-failed { color: var(--neon-pink); }

    .grade-display { margin-top: 20px; padding: 20px; border: 1px solid var(--neon-blue); background: rgba(0, 242, 255, 0.05); }
    .grade-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 15px 0; }
    .grade-box { border: 1px solid #333; padding: 10px; text-align: center; }
</style>
</head>
<body>

<div class="nav-bar">
    <button id="navBtn" onclick="openLogin()">Admin Access</button>
</div>

<div class="container">
    <div id="studentPortal" class="card">
        <h2>Student Inquiry Terminal</h2>
        <div style="display: flex; gap: 10px;">
            <input id="searchName" placeholder="ENTER FULL NAME" style="flex: 1;">
            <button onclick="searchStatus()">View Grades</button>
        </div>
        
        <div id="resultDisplay" class="grade-display" style="display:none;">
            <h3 id="res_name" style="color:var(--neon-blue); margin-top:0;"></h3>
            <p id="res_type" style="font-size: 0.8em; color: #888;"></p>
            <div class="grade-grid">
                <div class="grade-box">1st: <span id="res_g1"></span></div>
                <div class="grade-box">2nd: <span id="res_g2"></span></div>
                <div class="grade-box">3rd: <span id="res_g3"></span></div>
            </div>
            <div style="text-align:center; font-size:1.2em; font-weight:bold;">
                GPA: <span id="res_gpa"></span> | STATUS: <span id="res_status"></span>
            </div>
        </div>
    </div>

    <div id="adminPortal" class="card">
        <h2>Admin Control Unit</h2>
        <div class="form-grid">
            <input id="add_name" placeholder="STUDENT NAME">
            <select id="add_type">
                <option value="New Student">New Student</option>
                <option value="Old Student">Old Student</option>
            </select>
            <input id="add_g1" type="number" placeholder="1ST">
            <input id="add_g2" type="number" placeholder="2ND">
            <input id="add_g3" type="number" placeholder="3RD">
        </div>
        <div style="text-align: center;">
            <button onclick="saveNewStudent()">Register Entry</button>
            <button onclick="logout()" style="border-color:#555; color:#555;">Logout</button>
        </div>
        <table>
            <thead>
                <tr>
                    <th>UID</th>
                    <th>Name</th>
                    <th>Type</th>
                    <th>GPA</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="adminTableBody"></tbody>
        </table>
    </div>
</div>

<div id="editModal" class="modal">
    <div class="modal-content">
        <h3 style="color:var(--neon-blue); margin-top:0;">MOD_RECORDS</h3>
        <input type="hidden" id="edit_id">
        <div style="display:grid; gap:10px;">
            <input id="edit_name" placeholder="NAME">
            <select id="edit_type">
                <option value="New Student">New Student</option>
                <option value="Old Student">Old Student</option>
            </select>
            <input id="edit_g1" type="number" placeholder="1ST">
            <input id="edit_g2" type="number" placeholder="2ND">
            <input id="edit_g3" type="number" placeholder="3RD">
        </div>
        <div style="margin-top:20px; display:flex; gap:10px;">
            <button onclick="updateStudentRecord()" style="flex:1;">Update</button>
            <button onclick="closeEditModal()" style="flex:1; border-color:#555;">Cancel</button>
        </div>
    </div>
</div>

<div id="loginOverlay" class="modal">
    <div class="modal-content" style="width:300px; text-align:center;">
        <h3 style="color:var(--neon-blue)">ADMIN AUTH</h3>
        <input type="text" id="user" placeholder="USERNAME" style="width:80%; margin-bottom:10px;">
        <input type="password" id="pass" placeholder="PASSWORD" style="width:80%; margin-bottom:20px;">
        <button onclick="attemptLogin()">LOGIN</button>
    </div>
</div>

<script>
let isAdmin = false;

function openLogin() { document.getElementById('loginOverlay').style.display='flex'; }
function attemptLogin() {
    const u = document.getElementById('user').value;
    const p = document.getElementById('pass').value;
    fetch('/admin-login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username: u, password: p})
    }).then(res => {
        if(res.ok) { isAdmin=true; document.getElementById('loginOverlay').style.display='none'; showAdmin(); }
        else alert("DENIED");
    });
}
function showAdmin() {
    document.getElementById('studentPortal').style.display='none';
    document.getElementById('adminPortal').style.display='block';
    document.getElementById('navBtn').style.display='none';
    loadAdminData();
}
function logout() { location.reload(); }

function loadAdminData(){
    fetch('/students').then(res=>res.json()).then(data=>{
        let tbody = document.getElementById("adminTableBody");
        tbody.innerHTML = "";
        data.forEach(s=>{
            tbody.innerHTML += `<tr>
                <td>#${s.id}</td>
                <td>${s.name}</td>
                <td>${s.student_type}</td>
                <td>${s.gpa.toFixed(2)}</td>
                <td class="${s.status=='Passed'?'status-passed':'status-failed'}">${s.status.toUpperCase()}</td>
                <td>
                    <button style="border-color:#f1c40f; color:#f1c40f; padding:5px;" onclick='openEditModal(${JSON.stringify(s)})'>EDIT</button>
                    <button style="border-color:red; color:red; padding:5px;" onclick="deleteStudent(${s.id})">DEL</button>
                </td>
            </tr>`;
        });
    });
}

function searchStatus(){
    let query = document.getElementById("searchName").value;
    fetch('/search?name=' + encodeURIComponent(query)).then(res=>res.json()).then(data=>{
        let display = document.getElementById("resultDisplay");
        if(data.found) {
            display.style.display = "block";
            document.getElementById("res_name").innerText = data.name.toUpperCase();
            document.getElementById("res_type").innerText = "RECORD TYPE: " + data.type.toUpperCase();
            document.getElementById("res_g1").innerText = data.g1;
            document.getElementById("res_g2").innerText = data.g2;
            document.getElementById("res_g3").innerText = data.g3;
            document.getElementById("res_gpa").innerText = data.gpa.toFixed(2);
            document.getElementById("res_status").innerText = data.status.toUpperCase();
            document.getElementById("res_status").className = data.status == 'Passed' ? 'status-passed' : 'status-failed';
        } else {
            alert("No record found.");
            display.style.display = "none";
        }
    });
}

function openEditModal(s) {
    document.getElementById('edit_id').value = s.id;
    document.getElementById('edit_name').value = s.name;
    document.getElementById('edit_type').value = s.student_type;
    document.getElementById('edit_g1').value = s.grade1;
    document.getElementById('edit_g2').value = s.grade2;
    document.getElementById('edit_g3').value = s.grade3;
    document.getElementById('editModal').style.display = 'flex';
}
function closeEditModal() { document.getElementById('editModal').style.display = 'none'; }

function updateStudentRecord(){
    const id = document.getElementById('edit_id').value;
    fetch('/student/'+id, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            name: document.getElementById('edit_name').value,
            student_type: document.getElementById('edit_type').value,
            grade1: document.getElementById('edit_g1').value,
            grade2: document.getElementById('edit_g2').value,
            grade3: document.getElementById('edit_g3').value
        })
    }).then(() => { closeEditModal(); loadAdminData(); });
}

function saveNewStudent(){
    fetch('/student', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            name: document.getElementById("add_name").value,
            student_type: document.getElementById("add_type").value,
            grade1: document.getElementById("add_g1").value,
            grade2: document.getElementById("add_g2").value,
            grade3: document.getElementById("add_g3").value
        })
    }).then(() => { loadAdminData(); alert("Student Registered!"); });
}

function deleteStudent(id){ if(confirm("Delete?")) fetch('/student/'+id, {method:'DELETE'}).then(()=>loadAdminData()); }
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(html_page)

@app.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    if data.get('username') == ADMIN_USER and data.get('password') == ADMIN_PASS:
        return jsonify({"success": True})
    return jsonify({"success": False}), 401

@app.route('/students')
def get_students():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id":r[0],"name":r[1],"student_type":r[2],"grade1":r[3],"grade2":r[4],"grade3":r[5],"gpa":r[6],"status":r[7]} for r in rows])

@app.route('/search')
def search_student():
    name = request.args.get('name')
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, status, student_type, grade1, grade2, grade3, gpa FROM students WHERE name LIKE ?", (name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({
            "found": True, "name": row[0], "status": row[1], "type": row[2],
            "g1": row[3], "g2": row[4], "g3": row[5], "gpa": row[6]
        })
    return jsonify({"found": False})

@app.route('/student', methods=['POST'])
def add_student():
    data = request.get_json()
    g1, g2, g3 = float(data["grade1"]), float(data["grade2"]), float(data["grade3"])
    gpa = (g1 + g2 + g3) / 3
    status = "Passed" if gpa >= 75 else "Failed"
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name,student_type,grade1,grade2,grade3,gpa,status) VALUES (?,?,?,?,?,?,?)", 
                   (data["name"], data["student_type"], g1, g2, g3, gpa, status))
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
    cursor.execute("UPDATE students SET name=?, student_type=?, grade1=?, grade2=?, grade3=?, gpa=?, status=? WHERE id=?", 
                   (data["name"], data["student_type"], g1, g2, g3, gpa, status, id))
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
