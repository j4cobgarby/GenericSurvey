from flask import Flask, abort, redirect, url_for, render_template, current_app, g, request, session, flash
from getpass import getpass
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

import click
import sqlite3 as sql

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

def get_db():
    if "db" not in g:
        print(f'Connecting to db {current_app.config["DATABASE"]}')
        g.db = sql.connect(current_app.config["DATABASE"], detect_types=sql.PARSE_DECLTYPES)
        g.db.row_factory = dict_factory
    return g.db

def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()

def create_app():
    app = Flask(__name__)
    app.config["DATABASE"] = "survey.sqlite"
    app.secret_key = '694a8d6908793fab61cf8eae63a81a9e6f80af12e234a56e4ac994062d305938'

    app.teardown_appcontext(close_db)

    print("App initialised")
    return app

def safeformget(s):
    if s in request.form:
        return request.form[s]
    else:
        return None

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "is_admin" not in session or not session["is_admin"]:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated

app = create_app()

@app.cli.command("dbinit")
def init_database():
    with current_app.open_resource("schema.sql") as f:
        get_db().executescript(f.read().decode("utf-8"))
    click.echo("Initialised database successfully.")

@app.cli.command("set_password")
def set_password():
    pw_plain = getpass("Pick new administrator password: ")

    with open("passwd", "w") as pw_file:
        pw_file.write(generate_password_hash(pw_plain))
        print("Written hash to 'passwd'")


@app.route("/")
def root():
    cur = get_db().cursor()

    surveys = cur.execute("SELECT * FROM surveys").fetchall()
    
    return render_template("homepage.html", surveys=surveys)

@app.get("/login")
def show_login():
    return render_template("admin_login.html")

@app.post("/login")
def check_login():
    pw_plain = safeformget("pass")

    with open("passwd", "r") as pw_file:
        saved_hash = pw_file.readline()
        if (check_password_hash(password=pw_plain, pwhash=saved_hash)):
            print("Logged in!")
            session["is_admin"] = True
            return redirect("/admin")
        else:
            return redirect("/login")

@app.get("/logout")
def do_logout():
    session["is_admin"] = False
    return redirect("/")

@app.route("/s/<int:survey_id>")
def view_survey(survey_id):
    cur = get_db().cursor()

    survey_info = cur.execute("SELECT * FROM surveys WHERE id=?", (str(survey_id),)).fetchone()
    questions = cur.execute("SELECT * FROM questions WHERE in_survey=? ORDER BY position", (str(survey_id),)).fetchall()

    for q in questions:
        if q["qtype"] == "RADIO":
            q["radio_options"] = q["radio_options"].split(";")

    return render_template("view_survey.html", **survey_info, questions=questions)
    

@app.post("/s/<int:survey_id>/submit")
def submit(survey_id):
    print(survey_id, request.form)

    cur = get_db().cursor()

    cur.execute("UPDATE last_response_set SET id = id + 1")
    response_set = int(cur.execute("SELECT id FROM last_response_set").fetchone()['id'])
    
    for qid in request.form:
        cur.execute("INSERT INTO responses (question_id, response_set, answer) VALUES (?, ?, ?)", (qid, response_set, request.form[qid]))

    get_db().commit()

    return redirect("/")

@app.get("/s/new")
@requires_auth
def newsurvey_get():
    return render_template("new_survey.html")

@app.post("/s/new")
@requires_auth
def newsurvey_post():
    cur = get_db().cursor()

    if "num_questions" not in request.form:
        return "Form error";

    # First create new blank survey
    cur.execute("INSERT INTO surveys (title, descr) VALUES (?, ?);", 
        [safeformget("survey_title"), safeformget("survey_descr")]);
    survey_id = cur.lastrowid

    for q_i in range(int(request.form["num_questions"])):
        print("Inserting one question")
        ins = cur.execute("INSERT INTO questions (in_survey, position, title, descr, qtype, radio_options, integer_lb, integer_ub) VALUES\
            (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                survey_id, q_i, 
                safeformget(f"inp{q_i}title"), "", 
                safeformget(f"type{q_i}"), 
                safeformget(f"inp{q_i}options"), 
                safeformget(f"inp{q_i}lb"), 
                safeformget(f"inp{q_i}ub")
            ])

    get_db().commit()

    return redirect("/")

@app.get("/admin")
@requires_auth
def admin_panel():
    return render_template("admin.html")

@app.get("/results")
@requires_auth
def results_homepage():
    cur = get_db().cursor()
    surveys = cur.execute("SELECT * FROM surveys").fetchall()

    return render_template("results_list.html", surveys=surveys)

@app.get("/results/<int:survey_id>")
@requires_auth
def results_for(survey_id):
    cur = get_db().cursor()

    survey_info = cur.execute("SELECT * FROM surveys WHERE id = ?", (str(survey_id),)).fetchone()

    response_data = {}

    response_sets = cur.execute("SELECT DISTINCT r.response_set FROM responses AS r JOIN questions AS q ON r.question_id = q.id WHERE q.in_survey = ?", (str(survey_id),)).fetchall()
    for row in response_sets:
        rs = row['response_set']
        print("rs: ", str(rs))
        set_responses = cur.execute("SELECT q.id AS qid, r.answer, q.title AS question FROM responses AS r JOIN questions AS q ON r.question_id = q.id WHERE r.response_set = ?", (str(rs),)).fetchall()
        set_responses_dict = {r['qid']: r['answer'] for r in set_responses}
        response_data[rs] = set_responses_dict
    
    questions = cur.execute("SELECT id, title FROM questions WHERE in_survey = ? ORDER BY position", (str(survey_id),)).fetchall()

    return render_template("survey_results.html", response_data=response_data, survey_info=survey_info, questions=questions)

@app.get("/download/<int:survey_id>")
@requires_auth
def download_results(survey_id):
    cur = get_db().cursor()

    survey_info = cur.execute("SELECT * FROM surveys WHERE id = ?", (str(survey_id),)).fetchone()

    response_data = {}

    response_sets = cur.execute("SELECT DISTINCT r.response_set FROM responses AS r JOIN questions AS q ON r.question_id = q.id WHERE q.in_survey = ?", (str(survey_id),)).fetchall()
    for row in response_sets:
        rs = row['response_set']
        print("DEBUG", rs, response_sets)
        set_responses = cur.execute("SELECT q.id AS qid, r.answer, q.title AS question FROM responses AS r JOIN questions AS q ON r.question_id = q.id WHERE r.response_set = ?", (str(rs),)).fetchall()
        set_responses_dict = {r['qid']: r['answer'] for r in set_responses}
        response_data[rs] = set_responses_dict
    
    questions = cur.execute("SELECT id, title FROM questions WHERE in_survey = ? ORDER BY position", (str(survey_id),)).fetchall()
    questions_dict = {r['id']: r['title'] for r in questions}

    # return questions_dict

    return {
        "questions": questions_dict,
        "responses": [response_data[rs] for rs in response_data]
    }