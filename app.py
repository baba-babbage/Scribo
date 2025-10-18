from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
load_dotenv("hello.env")
PASSWORD = os.getenv("NOTEBOOK_PASSWORD", "kamikaze")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecret")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    notes = db.relationship("Note", backref="owner", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, default="")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

# Routes
@app.route("/", methods=["GET", "POST"])

#Login route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if User.query.filter_by(username=username).first():
            return "Username already exists!"
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            return redirect("/notes")
        else:
            return "Invalid credentials!"
    return render_template("login.html")


# Notes route

@app.route("/notes", methods=["GET", "POST"])
def notes():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    if request.method == "POST":
        title = request.form["title"]
        new_note = Note(title=title, user_id=user_id)
        db.session.add(new_note)
        db.session.commit()
        return redirect("/notes")

    all_notes = Note.query.filter_by(user_id=user_id).order_by(Note.timestamp.desc()).all()
    return render_template("notes.html", notes=all_notes)

# Edit note route
@app.route("/note/<int:id>", methods=["GET", "POST"])
def edit_note(id):
    if not session.get("logged_in"):
        return redirect("/")
    note = Note.query.get_or_404(id)
    if request.method == "POST":
        note.content = request.form.get("content")
        db.session.commit()
        return redirect("/notes")
    return render_template("edit_note.html", note=note)


# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    notes = db.relationship("Note", backref="owner", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, default="")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

# Delete note route

@app.route("/delete/<int:id>")
def delete(id):
    if not session.get("logged_in"):
        return redirect("/")
    note = Note.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    return redirect("/notes")

# Logout route

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/login")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
