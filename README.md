# JSW EVAC Project
JSW Employee Face Recognition – Evacuation & Attendance System
AI-Powered Employee Registration, Photo Capture & Real-Time Recognition

This project is an AI-driven employee recognition system designed for JSW (Jindal Steel Works) to automate:

Employee Registration

Guided Photo Capture

Embedding Generation (Face Vector Storage)

Live Attendance / Evacuation Monitoring

Automatic Employee Status Logging

The system uses DeepFace + MTCNN + FaceNet for face detection & recognition and Flask as the backend framework.

📌 1. Features Overview
🔹 Employee Registration

Add employee details (Name, Department, Auto-generated Employee ID)

Guided photo capture (10 automatic poses)

Face embedding generation using FaceNet

Storage of embeddings in photos/<empid>/embedding.npy

🔹 Guided Automatic Photo Capture

JS gives instructions:

Look Straight

Turn Left

Turn Right

Look Up

Look Down

Smile

Neutral Face

Move closer

Move back

Stay Still

Each frame is uploaded to backend via /api/upload_frame

After completion → /api/finish_registration

🔹 Real-Time Recognition (Attendance / Evacuation Mode)

Live camera stream

Per-frame embedding generation

Matching with stored embeddings

Logs:

Present

Unknown

Errors

Stores attendance records

🔹 Admin Dashboard

Employee List

Attendance Logs

Download Reports

Search / Filter

📌 2. Technology Stack
Component	Technology
Backend	Flask (Python)
AI Models	DeepFace, MTCNN, FaceNet
Embeddings	NumPy vector storage
Frontend	HTML, CSS, JS
Camera Access	WebRTC
Database (Optional)	SQLite / CSV logs
Deployment	Windows / Linux


3. System Architecture
Flow:

User Registers → enters Name, Department

System generates Employee ID

User Captures 10 guided photos

Backend extracts embeddings

Embedding saved → photos/<empid>/embedding.npy

During attendance:

Live video frames processed

Face detected using MTCNN

Embedding generated

Matched against stored index

Result logged

📌 4. Project Folder Structure
JSW Evac -V2/
│
├── backend/
│   ├── app.py
│   ├── services/
│   │   ├── face_engine.py
│   ├── templates/
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── register.html
│   │   ├── capture.html
│   │   ├── attendance.html
│   ├── static/
│   │   ├── style.css
│   │   ├── capture.js (optional)
│   │   ├── JSQ.png
│   ├── photos/
│   │   ├── <empid>/image0.jpg
│   │   └── <empid>/embedding.npy
│   ├── logs/
│   │   └── attendance.csv
│   └── requirements.txt
│
└── README.md



5. Installation & Setup Guide
Step 1: Install Python 3.9 (Recommended)

DeepFace + TensorFlow works best with Python 3.9.

Check version:

python --version

Step 2: Create Virtual Environment
python -m venv venv39


Activate:

Windows:
venv39\Scripts\activate

Step 3: Install Dependencies

Create a requirements.txt:

Flask
opencv-python
numpy==1.23.5
deepface==0.0.79
tensorflow==2.10.0
mtcnn
pillow


Install all:

pip install -r requirements.txt


⚠️ Important Compatibility Notes

NumPy must be < 2.0

TensorFlow 2.10 is last officially supported on Windows without GPU

Python 3.9 required

Step 4: Start the Flask Server
python app.py


Open in browser:

http://127.0.0.1:5000

📌 6. How Registration Flow Works
1️⃣ User enters Name + Department

→ Backend generates next employee ID using:

/api/get_next_id

2️⃣ User proceeds to Capture Page

Camera starts using WebRTC.

3️⃣ 10 Automatic Guided Captures

Each frame is uploaded:

POST /api/upload_frame


Saved in:

photos/<empid>/image_0.jpg
photos/<empid>/image_1.jpg
...

4️⃣ Embedding Generation

After final pose:

POST /api/finish_registration


Backend calls:

DeepFace.represent(model_name="Facenet")


Stores averaged embedding:

photos/<empid>/embedding.npy

📌 7. Attendance / Evacuation Flow

Start camera in attendance dashboard

Every frame sent to backend /api/scan

Backend:

Detects face

Extracts embedding

Matches with stored index

Returns:

Employee ID

Name

Department

Similarity Score

Logs stored in:

logs/attendance.csv

📌 8. API Endpoints
POST /register

Save user details.

GET /api/get_next_id

Generate new employee ID.

POST /api/upload_frame

Upload guided capture frame.

POST /api/finish_registration

Generate FaceNet embedding.

POST /api/scan

Live recognition for attendance.

📌 9. Troubleshooting
❗ TensorFlow Import Error

→ Use Python 3.9
→ Use TensorFlow 2.10

❗ NumPy errors (_ARRAY_API not found)

→ Install:

pip install numpy==1.23.5 --force-reinstall

❗ Camera Not Working

→ Check browser permissions
→ Ensure HTTPS in production

❗ FaceDetector import error

→ Use updated face_engine.py
→ Use DeepFace.detectors correctly

📌 10. Future Enhancements

Add Admin roles

Export reports in Excel

Add live CCTV multi-face recognition

Add geofencing attendance

Add mobile version (React Native)

Add cloud database (PostgreSQL)