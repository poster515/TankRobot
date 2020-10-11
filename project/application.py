import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, make_response, jsonify
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

if not DEV:
    from tank_cmd import left, right, forward, reverse, shot

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

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

@app.route("/", methods = ["GET", "POST"])
def index():
    """Show Home Page"""
    if request.method == "POST":
        # try to to grab user info from form and post it to DB
        try:
            # user_name=session["user_name"]
            # let's just use request object without session, not passing anything sensitive here
            user_name = request.form['username']
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
            # they have to wait. grab ip address and push to DB
            print("User {} must wait, IP = {}".format(user_name, request.remote_addr))
            db.execute("INSERT (:user_name, :ip_addr) INTO users", user_name=user_name, ip_addr=request.remote_addr)
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

    if request.cookies.get("user_name"):
        user_name = request.cookies.get("user_name")
    else:
        user_name = None

    if user_name is not None:
        # grab number of users ahead of this one
        num_users = 0
        for i in len(users):
             if users["user_name"] == user["user_name"]:
                 break
             else:
                 num_users += 1
        resp = make_response(render_template("wait.html", user_name=None, num_users=len(users)))
        resp.set_cookie("user_name", user_name)
        return render_template("wait.html", user_name=user_name, num_users=num_users)
    else:
        # if user not registered yet, just display total number of waitees
        users = db.execute("SELECT * from users")
        resp = make_response(render_template("wait.html", user_name=None, num_users=len(users)))
        return resp

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



def errorhandler(e):
    """Handle error"""
    flash(e)
    return redirect("/")

# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    # Configure application
    global app = Flask(__name__)

    # global double-ended queue for tank commands
    tank_cmd_queue = deque()

    # initialize new db connection and create the only table.
    # consist of [id][user_name][IP_address]
    # I think all we need is a relative db, don't really care about the absolute path
    database = "./tank_control.db"
    global db_conn = create_connection(database)
    if db_conn:
        create_table(db_conn, sql_table_func())
    else:
        print("Error creating table, exiting program.")
        sys.exit()


    # finally, as part of setup, call drive_tank. this function
    # constantly searches the tank_cmd_queue for commands, and then
    # executes them.
    drive_tank()
