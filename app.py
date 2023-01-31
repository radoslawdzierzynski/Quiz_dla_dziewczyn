import time
import os
import os.path
from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "static\\images"
ALLOWED_EXTENSIONS = ("png", "jpg", "jpeg", "gif")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SECRET_KEY"] = "secret_key"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
db = SQLAlchemy(app)


def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_answer(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))


def order_by_random(questions):
    q = [int(idx.strip()) for idx in session.get("questions").split() if idx.strip()]
    ret = None
    while not ret:
        q_filter = questions.query.filter(questions.id.not_in(q)).order_by(func.random()).first()
        if not q_filter:
            return []
        try:
            with open(str(q_filter.correct)) as f, open(str(q_filter.incorrect1)) as f1, open(str(q_filter.incorrect2)) as f2:
                ret = q_filter
        except FileNotFoundError as e:
            q.append(q_filter.id)
    return q_filter


def play(questions, session, request, name):
    if not session["questions"] and not order_by_random(questions):
        flash("Nie ma pytań \n Utwórz najpierw pytanie")
    if len(session["questions"]) < 20:
        if request.method == "POST":
            answer = request.form["answer"]
            if answer == "1":
                session["questions"] += f" {request.form['qid']}"
                time.sleep(0.7)
                return redirect(url_for("game"))
            if answer == "2":
                time.sleep(0.6)
                return redirect(url_for("game"))
        return render_template("game.html", name=name, pytanie=order_by_random(questions))
    else:
        return render_template("win.html")


class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    questions = db.Column(db.String, unique=True, nullable=False)
    correct = db.Column(db.String, nullable=False)
    incorrect1 = db.Column(db.String, nullable=False)
    incorrect2 = db.Column(db.String, nullable=False)
    audio_question = db.Column(db.String, nullable=False)


class Questions1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    questions = db.Column(db.String, unique=True, nullable=False)
    correct = db.Column(db.String, nullable=False)
    incorrect1 = db.Column(db.String, nullable=False)
    incorrect2 = db.Column(db.String, nullable=False)
    audio_question = db.Column(db.String, nullable=False)


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST" and request.form.get("cls"):
        session["questions"] = ""
    return render_template("index.html")


@app.route("/instruction")
def instruction():
    return render_template("instruction.html")


@app.route("/name_age", methods=["POST", "GET"])
def name_age():
    if request.method == "POST":
        name = request.form["name"]
        old = (request.form["old"])
        if name == "":
            flash("Proszę wpisz swoje imię.")
            return redirect(request.url)
        if old == "":
            flash("Proszę podaj ile masz lat.")
            return redirect(request.url)
        else:
            session["name"] = name
            session["old"] = old
            session["questions"] = ""
            return redirect(url_for("game"))
    return render_template("name_age.html")


@app.route("/game", methods=["POST", "GET"])
def game():
    name = session.get("name")
    old = session.get("old")
    if old <= "4":
        return play(questions=Questions, session=session, request=request, name=name)
    if old >= "5":
        return play(questions=Questions1, session=session, request=request, name=name)


@app.route("/make_questions", methods=["POST", "GET"])
def make_questions():
    if request.method == "POST":
        question = request.form["question"]
        answer1 = request.files["correct"]
        answer2 = request.files["incorrect1"]
        answer3 = request.files["incorrect2"]
        db_question = request.form["select"]
        audio_question = "static/music/1-second-of-silence.mp3"
        if question == "":
            flash("Nie wpisano pytania")
            return redirect(request.url)
        if answer1.filename == "":
            flash("Nie wybrano pliku do wgrania jako poprawna odpowiedź")
            return redirect(request.url)
        if answer2.filename == "" or answer3.filename == "":
            flash("Nie wybrano pliku do wgrania dla każdej odpowiedzi")
            return redirect(request.url)
        save_answer(answer1, answer2, answer3)
        path1 = f"static/images/{answer1.filename}"
        path2 = f"static/images/{answer2.filename}"
        path3 = f"static/images/{answer3.filename}"
        if db_question == "1":
            db.session.add(Questions(questions=question, correct=path1, incorrect1=path2, incorrect2=path3, audio_question=audio_question))
            db.session.commit()
            flash("Pytanie zostało dodane")
        if db_question == "2":
            db.session.add(Questions1(questions=question, correct=path1, incorrect1=path2, incorrect2=path3, audio_question=audio_question))
            db.session.commit()
            flash("Pytanie zostało dodane")
        return redirect(url_for("make_questions"))
    return render_template("make_questions.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
