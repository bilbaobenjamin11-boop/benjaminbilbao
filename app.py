from flask import Flask, jsonify, request, render_template_string
import sqlite3

app = Flask(__name__)
DATABASE = "students.db"

# Admin Credentials (Hardcoded for this version)
ADMIN_USER = "admin"
ADMIN_PASS = "cyber123"

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
<title>Cyber Grade Portal</title>
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
        background-size: 30px 30px;
        color: #fff;
        margin: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 40px 20px;
    }

    .container { width: 100%; max-width: 900px; }

    .card { 
        background: var(--card-bg); 
        padding: 30px; 
        border: 2px solid var(--neon-pink);
        box-shadow: 0 0 20px rgba(255, 0, 127, 0.3);
    }

    h2 { text-align: center; color: var(--neon-pink); letter-spacing: 5px; text-shadow: 0 0 10px var(--neon-pink); }

    .form-row { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 10px; margin-bottom: 20px; }

    input { 
        background: #000; border: 1px solid var(--neon-pink); padding: 12px; color: var(--neon-blue); outline: none;
    }

    input:focus { box-shadow: 0 0 10px var(--neon-blue); border-color: var(--neon-blue); }

    button { 
        padding: 10px 20px; background: transparent; color: var(--neon-pink); border: 2px solid var(--neon-pink);
        cursor: pointer; font-weight: bold; text-transform: uppercase; transition: 0.3s;
    }

    button:hover { background: var(--neon-pink); color: #000; box-shadow: 0 0 15px var(--neon-pink); }

    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th { border-bottom: 2px solid var(--neon-blue); color: var(--neon-blue); padding: 15px; text-transform: uppercase; }
    td { padding: 15px; text-align: center; border-bottom: 1px solid #222; }

    .status-passed { color: var(--neon-blue); text-shadow: 0 0 5px var(--neon-blue); }
    .status-failed { color: var(--neon-pink); text-shadow: 0 0 5px var(--neon-pink); }

    /* Login Modal Styles */
    #loginOverlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.9); display: none; justify-content: center; align-items: center; z-index: 1000;
    }

    .login-box {
        background: #111; padding: 40px; border: 2px solid var(--neon-blue); width: 300px; text-align: center;
    }

    .login-box input { width: 80%; margin-bottom: 15px; border-color: var(--neon-blue); }

    #adminPortal { display: none; }
    #studentPortal { display: block; }

    .nav-bar { width: 100%; max-width: 900px; display: flex; justify-content: flex-end; margin-bottom: 10px; }
</style>
</head>
<body>

<div class="nav-bar">
    <button id="navBtn" onclick="toggleAdminAccess()">Access Admin</button>
</div>

<div class="container">
    <div id="studentPortal" class="card">
        <h2>Student Inquiry Terminal</h2>
        <div style="display: flex; gap: 10px; justify-content: center;">
            <input id="searchName" placeholder="ENTER YOUR FULL NAME" style="flex: 1;">
            <button onclick="searchStatus()">Check Status</button>
        </div>
        <div id="resultDisplay" style="margin-top:20px; text-align:center; font-size:1.2em; display:none; padding:20px; border:1px dashed var(--neon-blue);"></div>
    </div>

    <div id="adminPortal" class="card">
        <h2>Admin Control Unit</h2>
        <input type="hidden" id="studentId">
        <div class="form-row">
            <input id="name" placeholder="IDENT_NAME">
            <input id="g1" type="number" placeholder="1ST_GRD">
            <input id="g2" type="number" placeholder="2ND_GRD">
            <input id="g3" type="number" placeholder="3RD_GRD">
        </div>
        <div style="text-align: center; margin-bottom: 20px;">
            <button id="saveBtn" onclick="saveStudent()">Execute Entry</button>
            <button onclick="logout()">Logout</button>
        </div>
        <table id="adminTable">
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
            <tbody id="adminTableBody"></tbody>
        </table>
    </div>
</div>

<div id="loginOverlay">
    <div class="login-box">
        <h3 style="color:var(--neon-blue)">ADMIN AUTH</h3>
        <input type="text" id="user" placeholder="USERNAME">
        <input type="password" id="pass" placeholder="PASSWORD">
        <br>
        <button onclick="attemptLogin()">LOGIN</button>
        <button onclick="closeLogin()" style="border-color:#555; color:#555;">CANCEL</button>
    </div>
</div>

<script>
let isAdminAuthenticated = false;

function toggleAdminAccess() {
    if (isAdminAuthenticated) {
        showAdmin();
    } else {
        document.getElementById('loginOverlay').style.display = 'flex';
    }
}

function closeLogin() {
    document.getElementById('loginOverlay').style.display = 'none';
}

function attemptLogin() {
    const u = document.getElementById('user').value;
    const p = document.getElementById('pass').value;

    fetch('/admin-login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username: u, password: p})
    })
    .then(res => res.json())
    .then(data => {
        if(data.success) {
            isAdminAuthenticated = true;
            closeLogin();
            showAdmin();
        } else {
            alert("ACCESS DENIED: INVALID CREDENTIALS");
        }
    });
}

function showAdmin() {
    document.getElementById('studentPortal').style.display = 'none';
    document.getElementById('adminPortal').style.display = 'block';
    document.getElementById('navBtn').style.display = 'none';
    loadAdminData();
}

function logout() {
    isAdminAuthenticated = false;
    document.getElementById('studentPortal').style.display = 'block';
    document.getElementById('adminPortal').style.display = 'none';
    document.getElementById('navBtn').style.display = 'block';
    document.getElementById('user').value = '';
    document.getElementById('pass').value = '';
}

// REST OF THE LOGIC
function loadAdminData(){
    fetch('/students')
    .then(res=>res.json())
    .then(data=>{
        let tbody = document.getElementById("adminTableBody");
        tbody.innerHTML = "";
        data.forEach(s=>{
            let statusClass = s.status === "Passed" ? "status-passed" : "status-failed";
            tbody.innerHTML += `<tr><td>#${s.id}</td><td>${s.name}</td><td>${s.grade1}</td><td>${s.grade2}</td><td>${s.grade3}</td><td>${s.gpa.toFixed(2)}</td><td class="${statusClass}">${s.status.toUpperCase()}</td><td><button style="border-color:#f1c40f; color:#f1c40f; padding:5px;" onclick='prepareEdit(${JSON.stringify(s)})'>EDIT</button><button style="border-color:red; color:red; padding:5px;" onclick="deleteStudent(${s.id})">DEL</button></td></tr>`;
        });
    });
}

function searchStatus(){
    let query = document.getElementById("searchName").value;
    fetch('/search?name=' + encodeURIComponent(query))
    .then(res => res.json())
    .then(data => {
        let display = document.getElementById("resultDisplay");
        display.style.display = "block";
        if(data.found) {
            let color = data.status === "Passed" ? "var(--neon-blue)" : "var(--neon-pink)";
            display.innerHTML = `NAME: ${data.name.toUpperCase()}<br>RESULT: <span style="color:${color}">${data.status.toUpperCase()}</span>`;
        } else {
            display.innerHTML = "IDENTITY NOT FOUND IN DATABASE";
        }
    });
}

function saveStudent(){
    let id = document.getElementById("studentId").value;
    let url = id ? '/student/' + id : '/student';
    fetch(url, {
        method: id ? 'PUT' : 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            name: document.getElementById("name").value,
            grade1: document.getElementById("g1").value,
            grade2: document.getElementById("g2").value,
            grade3: document.getElementById("g3").value
        })
    }).then(() => { loadAdminData(); clearInputs(); });
}

function prepareEdit(s){
    document.getElementById("studentId").value = s.id;
    document.getElementById("name").value = s.name;
    document.getElementById("g1").value = s.grade1;
    document.getElementById("g2").value = s.grade2;
    document.getElementById("g3").value = s.grade3;
    document.getElementById("saveBtn").innerText = "Update Entry";
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
    if(confirm("Confirm Deletion?")) fetch('/student/'+id, { method:'DELETE' }).then(() => loadAdminData());
}
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
    return jsonify([{"id":r[0],"name":r[1],"grade1":r[2],"grade2":r[3],"grade3":r[4],"gpa":r[5],"status":r[6]} for r in rows])

@app.route('/search')
def search_student():
    name = request.args.get('name')
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, status FROM students WHERE name LIKE ?", (name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({"found": True, "name": row[0], "status": row[1]})
    return jsonify({"found": False})

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
