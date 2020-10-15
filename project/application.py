import sqlite3
from flask import Flask, flash, redirect, render_template, request, url_for, session, make_response, jsonify
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from collections import deque
import time
import string
import os, sys

# import sql db functions (file should be in same directory)
from project.sql_funcs import create_connection, create_table, sql_table_func

# initialize new db connection and create the only table.
# consist of [id][user_name][IP_address]
database = "./tank_control.db"
db_conn = create_connection(database)
if db_conn:
    create_table(db_conn, sql_table_func())
else:
    print("Error creating table, exiting program.")
    sys.exit()

def create_app(DEV: bool = True):

    # control debug print statements (Flask does a lot of this anyway)
    DEBUG = True

    if not DEV:
        from tank_cmd import left, right, forward, reverse, shot

    # Configure application
    app = Flask(__name__)

    # Generate secret key for application
    app.secret_key = "chrimbusrobottankcontrol"
    # app.secret_key = os.urandom(24)
    #
    # app.config["SESSION_FILE_DIR"] = mkdtemp()
    app.config["SESSION_PERMANENT"] = False
    # app.config["SESSION_TYPE"] = "filesystem"

    wait_timeout = 2 * 60.0 # i.e., you have five minutes to start driving otherwise you get kicked out
    drive_timeout = 1 * 60.0
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
            try:
                # first make sure that the user in this browser/at this IP address
                # isn't trying to register again.
                user_name = session["user_name"]
                IP_addr = session["IP_addr"]
                print("User {} at {} attempted to register again.".format(user_name, IP_addr))
                return redirect(url_for("wait"))
            except:
                pass
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
                redirect(url_for("index"))

            # first check if the user already existsin DB, then redirect them to wait page.
            # need to create new connection, since connections are all thread-specific.
            db_conn = create_connection(database)
            exists = db_conn.cursor().execute("SELECT * FROM users WHERE user_name = ? AND IP_addr = ?", (user_name, request.remote_addr)).fetchall()

            if len(exists) > 0:
                # they already signed up and have to wait
                flash("Already added {} to queue! We'll let you know when it's your turn.".format(user_name))
                return redirect(url_for("wait"))

            # otherwise insert user and IP address into db
            db_conn.cursor().execute("INSERT INTO users VALUES (?, ?, 'False', 'False', 0, 0)", (user_name, request.remote_addr))
            db_conn.commit()

            # grab the user with the lowest id number
            (next_user, _, can_drive, _, can_drive_endtime, _) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
            while (can_drive == "True") and (can_drive_endtime >= (time.time() + wait_timeout)):
                # then this user has waited too long. YEET
                print("user {} has waited too long to start driving. SAD!".format(next_user))
                db_conn.cursor().execute("DELETE FROM users WHERE rowid = (SELECT min(rowid) FROM users);", (user_name, IP_addr))
                db_conn.commit()
                (next_user, _, can_drive, _, can_drive_endtime, _) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()

            print("Next driver eligible: {}".format(next_user))
            if next_user == user_name:
                # then this person can drive!
                print("{} can drive!".format(next_user))
                redirect(url_for("drive"))
            else:
                flash("Added {} to queue! We'll let you know when it's your turn.".format(user_name))
                return redirect(url_for("wait"))
            return redirect(url_for("drive"))

        # User reached route via GET
        else:
            # see if this user has already registered
            try:
                user_name=session["user_name"]
                print("User {} is already signed up and requested home page.".format(user_name))
                return render_template("index.html", user_name=user_name)

            except KeyError:
                # if not registered yet, just display the generic home page
                return render_template("index.html", user_name=None)


    @app.route("/time_left")
    def time_left():
        db_conn = create_connection(database)
        (next_user, next_user_IP, _, is_driving, _, drive_endtime) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
        try:
            # make sure it's this user
            user_name = session["user_name"]
            IP_addr = session["IP_addr"]
            assert next_user == user_name
            assert next_user_IP == IP_addr
            print("time_left: It is user {} at {}'s turn!!".format(user_name, IP_addr))
            if is_driving == "True":
                return { "seconds_left": drive_endtime - int(time.time()) }
            else:
                return { "seconds_left": drive_timeout }
        except:
            print("Not sure how someone got to this route...")
            return "nothing"


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
            # user_name not found in the session, has NO RIGHT to drive the Chrimbus Tank
            return redirect(url_for("index"))

        # grab the bottommost entry, and grab the user name and their IP
        (next_user, next_user_IP, _, is_driving, _, drive_endtime) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()

        try:
            # make sure it's this user
            assert next_user == user_name
            assert next_user_IP == IP_addr
            print("It is user {} at {}'s turn!!".format(user_name, IP_addr))

            if is_driving == "True": # if already driving, check if they've outstayed their driving welcome
                if drive_endtime > (time.time() + drive_timeout):
                    print("user must have come back to this page, and their turn is over. YEET")
                    db_conn.cursor().execute("DELETE FROM users WHERE user_name = ? and IP_addr = ?", (user_name, IP_addr))
                    db_conn.commit()
                    session.clear()
                    return render_template(url_for("index"))
                print("User {} at {} should already be driving!!".format(user_name, IP_addr))
            else: # update their status to "driving"
                print("User {} at {} can now drive!!".format(user_name, IP_addr))
                db_conn.cursor().execute("UPDATE users SET is_driving = 'True', drive_endtime = ? WHERE rowid = (SELECT min(rowid) FROM users);", (int(time.time()) + drive_timeout))
                db_conn.commit()
            return render_template("drive.html", user=user_name)

        except AssertionError:
            flash("It's not your turn to drive, {}!".format(user_name))
            print("Directing user {} at {} to wait, it's not their dang turn!!".format(user_name, IP_addr))
            return render_template("wait.html")

    @app.route("/check_turn")
    def check_turn():
        try:
            # try to remove that user from the DB
            user_name = session["user_name"]
            IP_addr = session["IP_addr"]
            print("Checking if it's {} from IP {}'s turn".format(user_name, IP_addr))
            db_conn = create_connection(database)
            # first assert that we were actually the next user, just in case
            (next_user, next_user_IP, _, _, _, _) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
            if next_user == user_name:
                print("It is in fact {} from IP {}'s turn!!!".format(user_name, IP_addr))
                return True

        except (KeyError, AssertionError):
            pass
        # if we're not next, or there's no session key, return false
        return False


    @app.route("/drive_timeout")
    def drive_timeout():

        try:
            # try to remove that user from the DB
            user_name = session["user_name"]
            IP_addr = session["IP_addr"]
            print("Deleting {} from IP {} from DB".format(user_name, IP_addr))
            db_conn = create_connection(database)
            # delete this user from the DB
            db_conn.cursor().execute("DELETE FROM users WHERE user_name = ? and IP_addr = ?", (user_name, IP_addr))
            db_conn.commit()

            # finally, update the time by which the next user must start driving for the next user
            db_conn.cursor().execute("UPDATE users SET can_drive='True', can_drive_endtime=? WHERE rowid = (SELECT min(rowid) FROM users);", (int(time.time()) + (2 * 60)))
            db_conn.commit()
            (next_user, next_user_IP, _, _, can_drive_endtime, _) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
            print("Set user {} at {}'s can_drive_endtime to {}".format(next_user, next_user_IP, can_drive_endtime))
        except KeyError:
            # user_name not found in the session
            flash("You haven't signed up yet!")
        # clear session data
        session.clear()
        return jsonify(dict(redirect='/'))

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

        if len(user_names) > 0:
            return render_template("wait.html", user_name=user_name, user_names=user_names)
        else:
            return render_template("wait.html", user_name=None, user_names=None)

    @app.route('/left_start')
    def left_start():
        db_conn = create_connection(database)
        try:
            user_name = session["user_name"]
            IP_addr = session["IP_addr"]
            (next_user, next_user_IP, _) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
            assert user_name == next_user
            assert next_user_IP == IP_addr
            print("User {} started turning left".format(user_name))
        except:
            print("non-registered user has requested to start")
        # javascript requires a return statement
        return "Success"

    @app.route('/left_stop')
    def left_stop():
        db_conn = create_connection(database)
        try:
            user_name = session["user_name"]
            IP_addr = session["IP_addr"]
            (next_user, next_user_IP, _) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
            assert user_name == next_user
            assert next_user_IP == IP_addr
            print("User {} stopped turning left".format(user_name))
        except:
            print("non-registered user has requested to stop")

        return "Success"

    @app.route('/right_start')
    def right_start():
        db_conn = create_connection(database)
        try:
            user_name = session["user_name"]
            IP_addr = session["IP_addr"]
            (next_user, next_user_IP, _) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
            assert user_name == next_user
            assert next_user_IP == IP_addr
            print("User {} started turning right".format(user_name))
        except:
            print("non-registered user has requested to start")
        # javascript requires a return statement
        return "Success"

    @app.route('/right_stop')
    def right_stop():
        db_conn = create_connection(database)
        try:
            user_name = session["user_name"]
            IP_addr = session["IP_addr"]
            (next_user, next_user_IP, _) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
            assert user_name == next_user
            assert next_user_IP == IP_addr
            print("User {} stopped turning right".format(user_name))
        except:
            print("non-registered user has requested to stop")

        return "Success"


    @app.route('/forward_start')
    def forward_start():
        db_conn = create_connection(database)
        try:
            user_name = session["user_name"]
            IP_addr = session["IP_addr"]
            (next_user, next_user_IP, _) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
            assert user_name == next_user
            assert next_user_IP == IP_addr
            print("User {} started going forward".format(user_name))
        except:
            print("non-registered user has requested to start")
        # javascript requires a return statement
        return "Success"

    @app.route('/forward_stop')
    def forward_stop():
        db_conn = create_connection(database)
        try:
            user_name = session["user_name"]
            IP_addr = session["IP_addr"]
            (next_user, next_user_IP, _) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
            assert user_name == next_user
            assert next_user_IP == IP_addr
            print("User {} stopped going forward".format(user_name))
        except:
            print("non-registered user has requested to stop")

        return "Success"

    @app.route('/reverse_start')
    def reverse_start():
        db_conn = create_connection(database)
        try:
            user_name = session["user_name"]
            IP_addr = session["IP_addr"]
            (next_user, next_user_IP, _) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
            assert user_name == next_user
            assert next_user_IP == IP_addr
            print("User {} started reversing".format(user_name))
        except:
            print("non-registered user has requested to start")
        # javascript requires a return statement
        return "Success"

    @app.route('/reverse_stop')
    def reverse_stop():
        db_conn = create_connection(database)
        try:
            user_name = session["user_name"]
            IP_addr = session["IP_addr"]
            (next_user, next_user_IP, _) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
            assert user_name == next_user
            assert next_user_IP == IP_addr
            print("User {} stopped reversing".format(user_name))
        except:
            print("non-registered user has requested to stop")

        return "Success"

    @app.route('/shot_start')
    def shot_start():
        db_conn = create_connection(database)
        try:
            user_name = session["user_name"]
            IP_addr = session["IP_addr"]
            (next_user, next_user_IP, _) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
            assert user_name == next_user
            assert next_user_IP == IP_addr
            print("User {} poured a shot!".format(user_name))
        except:
            print("non-registered user has requested to start")
        # javascript requires a return statement
        return "Success"

    def errorhandler(e):
        """Handle error"""
        flash(e)
        return redirect("/")

    # listen for errors
    for code in default_exceptions:
        app.errorhandler(code)(errorhandler)

    return app
