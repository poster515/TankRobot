import sqlite3
from flask import Flask, flash, redirect, render_template, request, url_for, session, make_response, jsonify
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from collections import deque
import string
import os, sys

# import sql db functions (file should be in same directory)
from sql_funcs import create_connection, create_table, sql_table_func

# bool for when we're doing dev work off the raspberry pi
DEV = True

# control debug print statements (Flask does a lot of this anyway)
DEBUG = True

if not DEV:
    from tank_cmd import left, right, forward, reverse, shot

# Configure application
app = Flask(__name__)

# Generate secret key for application
app.secret_key = os.urandom(24)
#
# app.config["SESSION_FILE_DIR"] = mkdtemp()
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"

# global double-ended queue for tank commands
tank_cmd_queue = deque()

# initialize new db connection and create the only table.
# consist of [id][user_name][IP_address]
# I think all we need is a relative db, don't really care about the absolute path
database = "./tank_control.db"
db_conn = create_connection(database)
if db_conn:
    create_table(db_conn, sql_table_func())
else:
    print("Error creating table, exiting program.")
    sys.exit()

# now create some tank drive specific callback functions.
# these are called from the javascript callback scripts on the
# drive.html page.
def drive_tank():
    while True:
        try:
            # grab next function to be executed
            command = tank_cmd_queue.pop() # pops from right
            if not DEV:
                command() # execute function
            else:
                print("Next tank command is: {}".format(command.__name__))
        except:
            # print("Waiting for tank command...")
            pass

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods = ["GET", "POST"])
def index():
    """Show Home Page"""
    if request.method == "POST":
        # try to to grab user info from form and post it to DB
        try:
            user_name = request.form['user_name']
            assert len(user_name) > 0
            session["user_name"] = user_name
            session["IP_addr"] = request.remote_addr
            print("User {} at {} requested to sign up to drive...".format(user_name, request.remote_addr))
            print("Type of name and IP are {} and {}".format(type(user_name), type(request.remote_addr)))
        except (AssertionError, KeyError):
            print("Could not obtain user name from form.")
            flash("Please enter a valid user name.")
            redirect(url_for("index"))

        # first check if the user already existsin DB, then redirect them to wait page.
        # need to create new connection, since connections are all thread-specific.
        db_conn = create_connection(database)
        cur = db_conn.cursor()
        exists = cur.execute("SELECT * FROM users WHERE user_name = ? AND IP_addr = ?", (user_name, request.remote_addr)).fetchall()

        if len(exists) > 0:
            # they have to wait
            flash("Already added {} to queue! We'll let you know when it's your turn.".format(user_name))
            return redirect(url_for("wait", user=user_name, IP_addr=request.remote_addr))

        # otherwise insert user and IP address into db
        db_conn.cursor().execute("INSERT INTO users VALUES (?, ?, null)", (user_name, request.remote_addr))
        db_conn.commit()

        # grab the user with the lowest id number
        next_user = db_conn.cursor().execute("SELECT user_name FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()[0]

        print("Next driver eligible: {}".format(next_user))
        if next_user == user_name:
            # then this person can drive!
            print("{} can drive!".format(next_user))
            redirect(url_for("drive"))
        else:
            flash("Added {} to queue! We'll let you know when it's your turn.".format(user_name))
            return redirect(url_for("wait"))
        return redirect(url_for("drive"))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # see if this user has already registered
        try:
            user_name=session["user_name"]
            print("User {} is already signed up and requested home page.".format(user_name))
            return render_template("index.html", user_name=user_name)

        except KeyError:
            # if not registered yet, just display the generic home page
            return render_template("index.html", user_name=None)

@app.route("/drive", methods = ["GET"])
def drive():
    db_conn = create_connection(database)

    user_name = ""
    IP_addr = ""
    try:
        user_name = session["user_name"]
        IP_addr = session["IP_addr"]
        print("User {} at IP {} has entered drive route".format(user_name, IP_addr))
    except KeyError:
        # user_name not found in the session, has NOT RIGHT to drive the Chrimbus Tank
        flash("You haven't signed up yet!")
        return redirect(url_for("index"))

    # grab the bottommost entry, and grab the user name and their IP
    (next_user, next_user_IP, _) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()[0]

    try:
        # make sure it's this user
        assert next_user == user_name
        assert next_user_IP == IP_addr
        flash("Thanks {}! It's your turn to drive!".format(user_name))
        # don't forget to remove that user from the DB
        db_conn.execute("DELETE FROM users WHERE user_name = ? and IP_addr = ?", (user_name, IP_addr))
        db_conn.commit()
        return render_template("drive.html", user=user_name)

    except AssertionError:
        flash("It's not your turn to drive, {}!".format(user_name))
        return render_template("drive.html")

@app.route("/drive_timeout")
def drive_timeout():
    # clear session data (i.e., user_name) and redirect to the home page
    session.clear()
    return redirect(url_for("/"))

@app.route("/wait")
def wait():

    try:
        user_name = session["user_name"]
    except KeyError:
        print("Wait: Could not find user_name in session.")
        user_name = None

    # grab all users currently waiting
    db_conn = create_connection(database)
    user_names = db_conn.cursor().execute("SELECT user_name FROM users").fetchall()

    if user_name is not None:
        # grab number of users ahead of this one
        num_users = 0
        for name in user_names:
             if name == user_name:
                 break
             else:
                 num_users += 1
        # should already have a session cookie with this user name
        return render_template("wait.html", user_name=user_name, num_users=num_users)
    else:
        return render_template("wait.html", user_name=None, num_users=len(user_names))

@app.route('/_left')
def left():
    if request.args.get('left', False, type=bool):
        tank_cmd_queue.appendleft(left)

@app.route('/_right')
def right():
    if request.args.get('right', False, type=bool):
        tank_cmd_queue.appendleft(right)

@app.route('/_forward')
def forward():
    if request.args.get('forward', False, type=bool):
        tank_cmd_queue.appendleft(forward)

@app.route('/_reverse')
def reverse():
    if request.args.get('reverse', False, type=bool):
        tank_cmd_queue.appendleft(reverse)

@app.route('/_shot')
def shot():
    if request.args.get('shot', False, type=bool):
        tank_cmd_queue.appendleft(shot)

def errorhandler(e):
    """Handle error"""
    flash(e)
    return redirect("/")

# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


if __name__ == "__main__":
    print("Attempting to start app...")
    # sess = Session()
    # sess.init_app(app)
    app.run(debug=True)

    # finally, as part of setup, call drive_tank. this function
    # constantly searches the tank_cmd_queue for commands, and then
    # executes them.
    # drive_tank()
else:
    print("Could not find entry point.")
