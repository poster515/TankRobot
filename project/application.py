from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, make_response, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
#----------------------------------------------------------------
import feedparser

from datetime import datetime, timedelta

import string
import os

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

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

@app.route("/")
def index():
    """Show Home Page"""

    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Password is incorrect.")
            return redirect("/login")


        # Remember which user has logged in
        session['user_id'] = rows[0]["user_id"]
        user_list.append(session['user_id'])

        print("Successfully logged in user: ")
        print(session['user_id'])

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    user_list.remove(session['user_id'])
    session.clear()

    return redirect("/")

    # Redirect user to login form
    # return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        user = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        email = db.execute("SELECT * FROM users WHERE email = :email", email=request.form.get("email"))

        if (not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation")
            or not request.form.get("first_name") or not request.form.get("last_name")):

            flash("Missing information.")
            return redirect("/register")

        elif request.form.get("password") != request.form.get("confirmation"):
            flash("Passwords do not match")
            return redirect("/register")

        elif len(email) > 0:
            flash("Email already exists, please use another.")
            return redirect("/register")

        elif not user:
            for char in string.punctuation:
                if char in request.form.get("password"):
                    for num in string.digits:
                        if num in request.form.get("password"):
                            user = db.execute("INSERT into users (first_name, last_name, username, hash, age, weight, sex, email, phone) VALUES (:first_name, :last_name, :username, :hash, :age, :weight, :sex, :email, :phone)",
                                first_name=request.form.get("first_name"),
                                last_name=request.form.get("last_name"),
                                username=request.form.get("username"),
                                hash=generate_password_hash(request.form.get("password")),
                                age=request.form.get("age"),
                                weight=request.form.get("weight"),
                                sex=request.form.get("sex"),
                                email=request.form.get("email"),
                                phone=request.form.get("phone"))

                            return render_template("login.html")
            flash("Password must contain at least one special character and one number")
            return redirect("/register")
        else:
            flash("Username already exists.")
            return redirect("/register")
    else:
        return render_template("register.html")


@app.route("/comps")
def competitions():
    rows = db.execute("SELECT * from comps WHERE 1")

    comp_details = []

    for row in rows:
        comp_details.append([row["name"], row["date"], row["comp_id"]])

    return render_template("comps.html", comp_details=comp_details)

@app.route("/reg_for_comp")
def reg_for_comp():

    comp_id = request.args.get("q")

    try:
        print(comp_id)
        row = db.execute("SELECT * from comps where comp_id=:comp_id", comp_id=comp_id)
        if row[0]["open"] == "False":
            flash("Registration for this competition has closed.")
            return redirect("/comps")
    except:
        flash("Competition ID not recognized.")
        return redirect("/comps")

    comp_details = []

    print(row[0]["name"])
    if len(row) == 1:
        # comp_id	name	date	address	city	state	zip
        comp_details.append([row[0]["name"], row[0]["date"], row[0]["address"], row[0]["city"], row[0]["state"], row[0]["zip"]])

        session["comp_id"] = comp_id
        return render_template("registration.html", comp_details=comp_details)

    else:
        flash("Error in competition registration.")
        return redirect("/comps")

@app.route("/competition_registration", methods=["POST", "GET"])
def competition_registration():

    #TODO: check to see if user is already registered for meet first

    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        age = request.form.get("age")
        sex = request.form.get("sex")
        weight = request.form.get("weight").split('kg')[1]
        email = request.form.get("email")

        if '@' not in email or '.com' not in email:
            flash("Incorrect email.")
            return redirect("/comps")

        user = db.execute("SELECT * from competitors WHERE (comp_id=:comp_id) and (first_name=:first_name) and (last_name=:last_name)",
            comp_id=session["comp_id"],
            first_name=first_name,
            last_name=last_name)

        if len(user) > 0:
            flash("User is already registered for this competition.")
            return redirect("/comps")

        try:
            if session["user_id"]:
                db.execute("INSERT into competitors (comp_id, first_name, last_name, weight, age, sex, email, user_id) VALUES (:comp_id, :first_name, :last_name, :weight, :age, :sex, :email, :user_id)",
                    comp_id = session["comp_id"],
                    first_name=first_name,
                    last_name=last_name,
                    weight=weight,
                    age=age,
                    sex=sex,
                    email=email,
                    user_id=session["user_id"])

            else:
                db.execute("INSERT into competitors (comp_id, first_name, last_name, weight, age, sex, email) VALUES (:comp_id, :first_name, :last_name, :weight, :age, :sex, :email)",
                    comp_id = session["comp_id"],
                    first_name=first_name,
                    last_name=last_name,
                    weight=weight,
                    age=age,
                    sex=sex,
                    email=email)

            print(first_name)
            return render_template("success.html")
        except:
            flash("Error during registration.")
            return redirect("/comps")

    else:
        return redirect("/comps")

@app.route("/members")
def members():

    rows = db.execute("SELECT * FROM competitors INNER JOIN comps on comps.comp_id = competitors.comp_id WHERE 1")

    users = []

    for row in rows:
        users.append([row["first_name"], row["last_name"], row["weight"], row["age"], row["name"], row["date"], row["comp_id"]])

    return render_template("members.html", users=users)

@app.route("/member_results")
def member_results():

    comp_id = request.args.get("comp_id")
    fname = request.args.get("fname")
    lname = request.args.get("lname")

    # user_info = db.execute("SELECT * FROM results INNER JOIN competitors on (competitors.user_id = results.user_id) and (competitors.comp_id = results.comp_id) INNER JOIN comps on comps.comp_id = results.comp_id WHERE (results.comp_id = :comp_id) and (results.first_name = :fname) and (results.last_name = :lname)",
    user_info = db.execute("SELECT * FROM results INNER JOIN competitors on (competitors.comp_id = results.comp_id) and (competitors.first_name = results.first_name) and (competitors.last_name = results.last_name) INNER JOIN comps on comps.comp_id = results.comp_id WHERE (results.comp_id = :comp_id) and (results.first_name = :fname) and (results.last_name = :lname)",
        comp_id=comp_id,
        fname=fname,
        lname=lname)

    if len(user_info) == 0:
        flash("Member did not compete or results have not been posted.")
        return redirect("/members")

    user = []

    user.append([fname, lname, user_info[0]["squat"], user_info[0]["bench"], user_info[0]["deadlift"],
        user_info[0]["name"], user_info[0]["age"], user_info[0]["weight"], user_info[0]["date"]])

    return render_template("results.html", user=user)

@app.route("/personal_results")
def personal_results():

    results = db.execute("SELECT * FROM results INNER JOIN comps on comps.comp_id = results.comp_id WHERE results.user_id = :user_id", user_id=session["user_id"])

    if len(results) == 0:
        flash("Member does not have any previous competition information.")
        return redirect("/")

    user_info = []

    for result in results:

        competitor = db.execute("SELECT * from competitors WHERE comp_id=:comp_id and user_id=:user_id", comp_id=result["comp_id"], user_id=session["user_id"])

        user_info.append([result["squat"], result["bench"], result["deadlift"], result["name"], result["date"], competitor[0]["weight"], competitor[0]["age"]])

    return render_template("personal_results.html", user_info=user_info, fname=results[0]["first_name"], lname=results[0]["last_name"])

@app.route("/comp_results")
def comp_results():

    comp_id = request.args.get("comp_id")

    results = db.execute("SELECT * FROM results WHERE (comp_id=:comp_id)", comp_id=comp_id)
    comp_name = db.execute("SELECT name FROM comps WHERE (comp_id=:comp_id)", comp_id=comp_id)


    if len(results) == 0:
        flash("Competition results have not been recorded/posted.")
        return redirect("/comps")

    users = []

    for result in results:
        user = db.execute("SELECT * FROM competitors WHERE (comp_id=:comp_id) and (first_name=:fname) and (last_name=:lname)",
            comp_id=comp_id,
            fname=result["first_name"],
            lname=result["last_name"])

        print(result["first_name"])

        users.append([result["first_name"], result["last_name"], user[0]["weight"], user[0]["age"], result["squat"], result["bench"], result["deadlift"]])


    return render_template("comp_results.html", users=users, comp_name=comp_name[0]["name"])

@app.route("/programs")
def programs():
    if "user_id" in session:
        user_id = session["user_id"]
        session.clear()
        session["user_id"] = user_id

    else:
        session.clear()
    return render_template("programs.html")

@app.route("/search_prog")
def search():
    """Search for places that match query"""

    program = request.args.get("q")
    print("Searching for program like: ")
    print(str(program))

    row = db.execute("SELECT * FROM program_names WHERE (program_name LIKE :pgm_name)", pgm_name=program + "%")
    try:
        print(row[0])
    except:
        print("Couldn't find program.")

    return jsonify(row)
    # return render_template("/")

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

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/settings_change", methods=["POST"])
def settings_change():

    if request.method == "POST":
        if request.form.get("email"):

            db.execute("UPDATE users SET email = :email WHERE user_id = :user_id", email=request.form.get("email"), user_id=session["user_id"])
            print("email entered")

        elif request.form.get("password"):
            if(request.form.get("password") != request.form.get("confirm_password")):
                flash("Passwords do not match.")
                return redirect("/settings")

            db.execute("UPDATE users SET hash = :hash WHERE user_id = :user_id", hash=generate_password_hash(request.form.get("password")), user_id=session["user_id"])
            print("new password entered")

        elif request.form.get("phone"):
            db.execute("UPDATE users SET phone = :phone WHERE user_id = :user_id", phone=request.form.get("phone"), user_id=session["user_id"])
            print("phone entered")

        elif request.form.get("bench1RM"):

            db.execute("UPDATE users SET bench_1RM = :bench1RM WHERE user_id = :id", bench1RM=request.form.get("bench1RM"), id=session["user_id"])
            print("new bench entered")

        elif request.form.get("squat1RM"):
            print(session["user_id"])
            db.execute("UPDATE users SET squat_1RM = :squat1RM WHERE user_id = :id", squat1RM=request.form.get("squat1RM"), id=session["user_id"])
            print("new squat entered")

        elif request.form.get("deadlift1RM"):
            db.execute("UPDATE users SET deadlift_1RM = :deadlift1RM WHERE user_id = :id", deadlift1RM=request.form.get("deadlift1RM"), id=session["user_id"])
            print("new deadlift entered")

        else:
            flash("Error processing form, please try again.")
            return redirect("/setttings")

            print("no data entered")
    return render_template("success.html")

@app.route("/rss")
def rss():

    try:
        feed = feedparser.parse("https://www.jtsstrength.com/articles/category/weightlifting/feed/")
    except:
        flash("Could not open RSS feed.")
        return redirect("/")

    rss = []
    print(len(feed.entries))
    for i in range(0, len(feed.entries)):

        title = feed['entries'][i]['title']
        print(title)
        link = feed['entries'][i]['link']
        desc_start = feed['entries'][i]['description'].find("<p>")
        desc_finish = feed['entries'][i]['description'].find("</p>")
        desc = feed['entries'][i]['description'][desc_start + 3: desc_finish]

        rss.append([title, link, desc])

    print(len(rss))
    return render_template("rss.html", rows = rss)

def errorhandler(e):
    """Handle error"""
    flash(e)
    return redirect("/")

# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)