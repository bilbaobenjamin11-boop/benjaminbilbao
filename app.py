from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route('/')
def home():
  return "Welcome to my Flask API!"

@app.route('/student')
def get_student():
  return jsonify({
    "name": "BNJ",
    "grade": 3,
    "section": "BSIT-2 ARDUINO"
  })
