import sqlite3
from sqlite3 import Error
from flask import Flask, flash, redirect, render_template, request, session, make_response, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
#----------------------------------------------------------------
import feedparser
from projects.sql_funcs import * #
from datetime import datetime, timedelta

import string
import os, sys

user_list = []

# Configure application
app = Flask(__name__)

# Generate secret key for application
app.secret_key = os.urandom(24)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

# initialize new db connection and create the only tale.
# consist of [id][user_name][device specific something (IP address?)]
# database = r"C:\sqlite\db\pythonsqlite.db"
# I think all we need is a relative db, don't really care about the absolute path
database = r"./sqlite.db"
db_conn = create_connection(database)
if db_conn:
    create_table(db_conn, sql_table_func())
else:
    print("Error creating table, exiting program.")
    sys.exit()

@app.route("/", methods = ["GET", "POST"])
def index():
    """Show Home Page"""
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # try to to grab user info from form and post it to DB
        try:
            user_name=session["user_name"]
        except KeyError:
            # not sure how this could break but oh well
            flash("Could not find user name - please enter a valid user name.")
            redirect("/")

        # first, check if there any users waiting already
        users = db.execute("SELECT * from users")
        if len(users) == 0:
            # then this person can drive!
            redirect("/drive")
        else:
            # they have to wait.
            db.execute("INSERT :user_name INTO users", user_name=user_name)
            flash("Added {} to queue! We'll let you know when it's your turn.".format(user_name))
            return redirect("/wait")
        return redirect("/drive")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # see if this user has already registered
        try:
            user_name=session["user_name"]
            return render_template("index.html", user_name=user_name)
        except KeyError:
            # if not registered yet, just display the generic home page
            return render_template("index.html", user_name=None)

@app.route("/wait")
def wait():
    # grab all users currently waiting
    users = db.execute("SELECT * from users")

    try:
        user_name=session["user_name"]
        # grab number of users ahead of this one
        num_users = 0
        for i in len(users):
             if users["user_name"] == user["user_name"]:
                 break
             else:
                 num_users += 1
        return render_template("wait.html", user_name=user_name, num_users=num_users)
    except KeyError:
        # if user not registered yet, just display total number of waitees
        users = db.execute("SELECT * from users")
        return render_template("wait.html", user_name=None, num_users=len(users))

@app.route("/history")
def history():
    # TODO: display the history from all users
    rows = db.execute("SELECT * FROM competitors INNER JOIN comps on comps.comp_id = competitors.comp_id WHERE 1")

    users = []

    for row in rows:
        users.append([row["first_name"], row["last_name"], row["weight"], row["age"], row["name"], row["date"], row["comp_id"]])

    return render_template("members.html", users=users)

@app.route("/drive", methods = ["GET"])
def drive():
    # display the control icons for driving the tank
    try:
        # get current user name
        user_name = session["user_name"]

        # get next entry in db
        next_user_name = db.execute("SELECT * ")

        # make sure it's this user
        assert next_user_name["user_name"] == user_name

        # don't forget to remove that user from the DB
        db.execute("REMOVE :user_name from users", user_name = user_name)

        flash("Thanks {}! It's your turn to drive!".format(user_name))
        return render_template("drive.html", user=user_name)

    except (KeyError, AssertionError):
        flash("Sorry, you can't skip the line!".format(user_name))
        return redirect("/wait")


@app.route("/prog_details")
def prog_details():

    if "program" not in session or session["program"] == None:
        print("No session cookie named 'program'.")

        session["program"] = request.args.get("q")
        rows = db.execute("SELECT * FROM programs INNER JOIN program_names on program_names.program_num = programs.program_num INNER JOIN exercise_names on exercise_names.exercise_num = programs.exercise_num WHERE program_names.program_name = :sug and programs.week = '1'",
        sug=request.args.get("q"))

        print("Established cookie named 'program'.")

        program_details = []
        # day	sets	reps	percent_max	RPE	exercise_num	program_num	week	program_name	exercise_name
        for row in rows:
            print(row["day"])
            program_details.append([row["day"], row["sets"], row["reps"], row["percent_max"], row["RPE"], row["week"], row["program_name"], row["exercise_name"]])

        try:
            print("attempting to print webpage")
            return render_template("program_details.html", program_details=program_details)

        except:
            print("Could not obtain search criteria.")
            return render_template("programs.html")

    else:
        print("Session cookie named 'program' EXISTS!")
        # TODO: find way to get users 1RM for each exercise and provide them to user

        rows = db.execute("SELECT * FROM programs INNER JOIN program_names on program_names.program_num = programs.program_num INNER JOIN exercise_names on exercise_names.exercise_num = programs.exercise_num WHERE program_names.program_name = :sug and programs.week = :week",
            sug=session["program"],
            week=request.args.get("q"))
        return jsonify(rows)

def errorhandler(e):
    """Handle error"""
    flash(e)
    return redirect("/")

# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
