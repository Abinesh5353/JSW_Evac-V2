# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from pathlib import Path
import sqlite3
import os

from models.db import init_db, DB_PATH
from services.face_engine import load_model, get_embedding

DEPT_CODES = {
    "Iron Zone": "IRZ",
    "Sinter Plant": "SIN",
    "Coke Oven Plant": "COP",
    "Blast Furnace": "BLF",
    "Steel Melt Shop (SMS)": "SMS",
    "Ladle Refining Furnace (LRF)": "LRF",
    "Vacuum Degassing (VD)": "VD",
    "Continuous Casting Machine (CCM)": "CCM",
    "Blooming Mill": "BLM",
    "Bar & Rod Mill (BRM)": "BRM",
    "Annealing Unit": "ANL",
    "Bright Bar Unit": "BBU",
    "Air Separation Plant (ASP)": "ASP",
    "Captive Power Plant (CPP)": "CPP",
    "Gas Plant": "GAS",
    "Water Treatment Plant": "WTP",
    "Wastewater Treatment Plant": "WWT",
    "Material Handling & Logistics": "LOG",
    "Human Resources (HR)": "HR",
    "Finance & Accounts": "FIN",
    "Safety, Health & Environment (SHE)": "SHE",
    "Maintenance Department": "MNT",
    "Production Planning & Control (PPC)": "PPC",
    "Quality Assurance / Quality Control (QA/QC)": "QAQ",
    "Information Technology (IT)": "IT",
    "Administration": "ADM",
}
# ------------------------
# PATH SETUP
# ------------------------
BASE = Path(__file__).resolve().parent
TEMPLATES = BASE / "templates"
STATIC = BASE / "static"
PHOTOS = BASE / "photos"

# ------------------------
# FLASK APP (IMPORTANT: Only ONE app = FIXED)
# ------------------------
app = Flask(__name__, template_folder=str(TEMPLATES), static_url_path="/static")
app.secret_key = "jsw-secret-key"

# Ensure photos folder exists
PHOTOS.mkdir(exist_ok=True)

# ------------------------
# INITIALIZE DATABASE + AI MODEL
# ------------------------
init_db()
load_model()
from services.face_engine import build_index, INDEX

# Load embeddings at startup
INDEX.clear()
INDEX.update(build_index(str(PHOTOS)))

# ------------------------
# DATABASE CONNECTION
# ------------------------
def get_db_conn():
    return sqlite3.connect(DB_PATH)

# ------------------------
# ROUTES
# ------------------------

@app.route("/")
def home():
    if "admin" not in session:
        return redirect("/login")
    return render_template("index.html", present=0, missing=0, unknown=0, data=[])

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    print("USERNAME:", username)
    print("PASSWORD:", password)

    if username == "admin" and password == "1234":
        session["admin"] = True
        return redirect("/")

    return render_template("login.html", error="Invalid credentials")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ------------------------
# REGISTER EMPLOYEE
# ------------------------
@app.route("/register", methods=["GET","POST"])
def register():
    if "admin" not in session:
        return redirect("/login")

    if request.method == "POST":
        name = request.form.get("name")
        dept = request.form.get("department")

        # Get dept code
        dept_code = DEPT_CODES.get(dept, "GEN")

        con = get_db_conn()
        cur = con.cursor()

        # count employees with same dept
        cur.execute("SELECT COUNT(*) FROM employees WHERE department=?", (dept,))
        count = cur.fetchone()[0] + 1

        empid = f"JSW{dept_code}{count:03d}"

        folder = PHOTOS / empid
        folder.mkdir(exist_ok=True)

        cur.execute(
            "INSERT INTO employees(emp_id,name,department,folder_path) VALUES (?,?,?,?)",
            (empid, name, dept, str(folder)),
        )

        con.commit()
        con.close()

        return redirect(url_for("capture_page", empid=empid))

    return render_template("register.html")
@app.route("/api/get_next_id")
def get_next_id():
    try:
        dept = request.args.get("department")
        if not dept:
            return jsonify({"error": "missing department"}), 400

        dept_code = DEPT_CODES.get(dept, "GEN")

        con = get_db_conn()
        cur = con.cursor()

        # Check if department column exists
        try:
            cur.execute("SELECT COUNT(*) FROM employees WHERE department=?", (dept,))
            count = cur.fetchone()[0] + 1
        except:
            return jsonify({"error": "DB column issue"}), 500

        empid = f"JSW{dept_code}{count:03d}"

        return jsonify({"empid": empid})

    except Exception as e:
        print("ERROR in get_next_id:", e)
        return jsonify({"error": "server error"}), 500

# CAPTURE IMAGES PAGE
# ------------------------
@app.route("/register/capture/<empid>")
def capture_page(empid):
    return render_template("capture.html", empid=empid)

# ------------------------
# API - SAVE CAPTURED IMAGES
# ------------------------
@app.route("/api/upload_frame", methods=["POST"])
def upload_frame():
    empid = request.form.get("empid")
    index = request.form.get("index")
    frame = request.files.get("frame")

    if not empid or not frame:
        return jsonify({"error": "missing"}), 400

    folder = PHOTOS / empid
    folder.mkdir(exist_ok=True)

    filename = folder / f"img_{index}.jpg"
    frame.save(str(filename))

    return jsonify({"success": True, "file": str(filename)})
from services.face_engine import generate_employee_embedding, build_index

@app.route("/api/finish_registration", methods=["POST"])
def finish_registration():
    empid = request.form.get("empid")

    if not empid:
        return jsonify({"error": "Missing empid"}), 400

    success, msg = generate_employee_embedding(empid, str(PHOTOS))

    # Rebuild memory index so attendance can detect this employee
    build_index(str(PHOTOS))

    return jsonify({"success": success, "message": msg})

@app.route("/api/generate_embedding")
def generate_embedding():
    import numpy as np

    empid = request.args.get("empid")
    if not empid:
        return {"success": False, "error": "Missing empid"}

    folder = PHOTOS / empid

    # Load captured images
    images = sorted(folder.glob("img_*.jpg"))
    if len(images) == 0:
        return {"success": False, "error": "No images found"}

    emb_list = []

    for img_path in images:
        emb = get_embedding(str(img_path))
        if emb is not None:
            emb_list.append(emb)

    if len(emb_list) == 0:
        return {"success": False, "error": "No valid faces"}

    # Average embedding
    final_emb = np.mean(emb_list, axis=0)

    # Save embedding
    np.save(folder / "embedding.npy", final_emb)

    return {"success": True}

# ------------------------
# EVAC MODE
# ------------------------
@app.route("/evac_mode")
def evac_mode():
    if "admin" not in session:
        return redirect("/login")
    return render_template("evac_mode.html")


# ------------------------
# ATTENDANCE PAGE
# ------------------------
@app.route("/attendance")
def attendance():
    if "admin" not in session:
        return redirect("/login")
    return render_template("attendance.html")
@app.route("/api/scan_face", methods=["POST"])
def scan_face():
    try:
        img_file = request.files.get("frame")
        if img_file is None:
            return jsonify({"error": "no_frame"}), 400

        import numpy as np, cv2

        # Convert image bytes → numpy frame
        image_bytes = np.frombuffer(img_file.read(), np.uint8)
        frame = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({"error": "invalid_image"}), 400

        # Get DeepFace embedding
        embedding = get_embedding(frame[:, :, ::-1])  # BGR → RGB
        if embedding is None:
            return jsonify({"error": "no_face"}), 200

        # Match with stored employees
        from services.face_engine import match_embedding, INDEX
        empid, score = match_embedding(INDEX, embedding)

        return jsonify({
            "success": True,
            "match": empid,
            "confidence": float(score)
        })

    except Exception as e:
        print("ERROR in scan_face:", e)
        return jsonify({"error": "server_error"}), 500

# RUN SERVER
# ------------------------
if __name__ == "__main__":
    print("TEMPLATES:", TEMPLATES)
    print("STATIC:", STATIC)
    print("PHOTOS:", PHOTOS)
    app.run(host="0.0.0.0", port=5000, debug=True)
