from email.mime import base
from sqlalchemy.exc import IntegrityError

from os import urandom

from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI
from flask_cors import CORS
from flask import request, redirect, render_template, flash, session, url_for
from database import User, PreProcessedData, Session
import bcrypt

from functools import wraps

import os
import PyPDF2
import requests
import docx
from flask import Flask, request, jsonify

from flask import Flask, request, jsonify
import sqlite3

info = Info(title="ChatBot to database API :o", version="1.0.0")
app = OpenAPI(__name__, info=info)
app.config['SECRET_KEY'] = urandom(12)
CORS(app)

# home
@app.route('/')
def home():
    return redirect('/login')

# wrapper that verifies login
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first')
            return redirect('/login')
    return wrap

# login
@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['submit'] == 'Sign up':
            return redirect('/sign_up')
        if validateLogin(request.form['username'], request.form['password']):
            session['logged_in'] = True
            if 'email' not in session:
                session['email'] = request.form['username']
            return redirect('/chatbot')
        else:
            error = 'Invalid email or password'
            flash(error)
    return render_template('login.html', error=error)

# sign up
@app.route('/sign_up', methods=['POST', 'GET'])
def sign_up():
    error = None
    if request.method == 'POST':
        if request.form['submit'] == "Confirmar":
            if request.form['password'] == request.form['senha_confirma']:
                session = Session()
                new_user = User(request.form['username'], bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt()))
                try:
                    session.add(new_user)
                    session.commit()
                    return redirect('/login')
                except IntegrityError as e:
                    error = "Email already registered"
            else:
                error = "Passwords don't match"
        else:
            return redirect('/')
    return render_template('cadastro.html', error=error)

# chatbot
@app.route('/chatbot', methods=['GET'])
# @login_required
def chatbot():
    error = None
    return render_template('chatbot.html', error = error)

# logout
@app.route('/logout', methods=['GET'])
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('email', None)
    return redirect('/login')

# validate login
def validateLogin(email, password):
    sessionBD = Session()
    query = sessionBD.query(User).filter(User.email == email)
    result = query.first()
    if result:
        if bcrypt.checkpw(password.encode('utf-8'), result.password):
            return True
    return False

@app.route('/extract-answer-from-file', methods=['POST'])
def extract_answer_from_file():
    data = request.json
    filePath = data['filePath']
    question = data['question']

    raw_text = get_raw_text_from_file(filePath)
    answerFromChatGpt = get_chat_gpt_answer(raw_text, question)

    return answerFromChatGpt

def get_raw_text_from_file(filePath):
    if not os.path.exists(filePath):
        raise FileNotFoundError(f"File '{filePath}' does not exist.")

    if filePath.endswith('.pdf'):
        with open(filePath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            raw_text = ''
            for page in reader.pages:
                raw_text += page.extract_text()

    elif filePath.endswith('.docx'):
        doc = docx.Document(filePath)
        raw_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])

    else:
        raise TypeError(f"File '{filePath}' has an unsupported extension.")

    return raw_text

def get_chat_gpt_answer(raw_text, question):
    message = {
        "message": f"{raw_text} {question}",
    }

    response = requests.post("http://localhost:3000/send-question-gpt", json=message)

    if response.status_code == 200:
        return {"answer": response.json()["answer"]}
    else:
        raise Exception(f"Request failed with status code {response.status_code}")

@app.route('/process-keywords', methods=['POST'])
def process_keywords():
    data = request.json
    keywords = data['keywords']
    keywords = keywords.lower()
    keywordsArray = keywords.split(",")
    db_response = find_best_match(keywordsArray)

    return jsonify(db_response)

def find_best_match(keywordsArray):
    db_results = query_database()

    db_results_dict = {}
    for filePath, fileLink, keyWords in db_results:
        db_results_dict.setdefault(filePath, []).append(keyWords)

    best_path = None
    max_intersection = 0

    for filePath, keyWordsList in db_results_dict.items():
        intersection_size = len(set(keyWordsList).intersection(keywordsArray))

        if intersection_size > max_intersection:
            max_intersection = intersection_size
            best_path = filePath

    return best_path

def query_database():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    cursor.execute("SELECT filePath, fileLink, keyword FROM 'pre-processed data'")
    results = cursor.fetchall()
    conn.close()
    return results