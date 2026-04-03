import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

database_url = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-fallback-key')

db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        task_content = request.form.get("task")
        if task_content and task_content.strip():
            new_task = Task(content=task_content.strip())
            db.session.add(new_task)
            db.session.commit()
        return redirect(url_for("home"))
    tasks = Task.query.all()
    return render_template("index.html", tasks=tasks)

@app.route("/delete/<int:task_id>")
def delete(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for("home"))

@app.route("/db-check")
def db_check():
    tasks = Task.query.all()
    return f"Total tasks in database: {len(tasks)} — Tasks: {[t.content for t in tasks]}"

# ✅ NEW — Update route
@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit(task_id):
    task = Task.query.get(task_id)
    if request.method == "POST":
        new_content = request.form.get("task")
        if new_content and new_content.strip():
            task.content = new_content.strip()
            db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", task=task)

if __name__ == "__main__":
    app.run(debug=True)