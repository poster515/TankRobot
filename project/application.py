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
import threading

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

def create_app(DEV: bool = True, wait_timeout: int = 60, drive_timeout: int = 60):

    # control debug print statements (Flask does a lot of this anyway)
    DEBUG = True

    #Definition of  motor pins
    IN1 = 20 # Motor A, pin2
    IN2 = 21 # Motor A, pin1
    IN3 = 19 # Motor B, pin2
    IN4 = 26 # Motor B, pin1
    ENA = 16 # Motor A, PWM
    ENB = 13 # Motor B, PWM
    PUMP = 2 # IO2 is the fan output

    if not DEV:
        import RPi.GPIO as GPIO
        import project.shot as shot
        #Set the GPIO port to BCM encoding mode
        GPIO.setmode(GPIO.BCM)
        #Ignore warning information
        GPIO.setwarnings(False)
        GPIO.setup(ENA,GPIO.OUT,initial=GPIO.HIGH)
        GPIO.setup(IN1,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(IN2,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(ENB,GPIO.OUT,initial=GPIO.HIGH)
        GPIO.setup(IN3,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(IN4,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(PUMP,GPIO.OUT,initial=GPIO.HIGH)
        pwm_ENA = GPIO.PWM(ENA, 2000)
        pwm_ENB = GPIO.PWM(ENB, 2000)
        pwm_ENA.start(0)
        pwm_ENB.start(0)

    # Configure application
    app = Flask(__name__)

    # Generate secret key for application
    app.secret_key = "chrimbusrobottankcontrol"
    # app.secret_key = os.urandom(24)
    #
    # app.config["SESSION_FILE_DIR"] = mkdtemp()
    app.config["SESSION_PERMANENT"] = False
    # app.config["SESSION_TYPE"] = "filesystem"

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
            while (can_drive == "True") and (can_drive_endtime < time.time()):
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
        """
            Function called from drive.html which returns the time in seconds
            available for the driver to maintain control.
        """
        db_conn = create_connection(database)

        try:
            # make sure it's this user
            (next_user, next_user_IP, _, is_driving, _, drive_endtime) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
            user_name = session["user_name"]
            IP_addr = session["IP_addr"]
            assert next_user == user_name
            assert next_user_IP == IP_addr
            if is_driving == "True":
                return jsonify(end_time = drive_endtime)
            else:
                return jsonify(end_time = drive_timeout)
        except:
            db_conn.cursor().execute("DELETE FROM users WHERE rowid = (SELECT min(rowid) FROM users);", (user_name, IP_addr))
            db_conn.commit()
            print("Not sure how someone got to this time_left route...")
            session.clear()
            return jsonify(dict(redirect='/'))


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

        try:
            (next_user, next_user_IP, can_drive, is_driving, candrive_endtime, drive_endtime) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
            # make sure it's this user
            assert next_user == user_name
            assert next_user_IP == IP_addr
            print("It is user {} at {}'s turn!!".format(user_name, IP_addr))
            try:
                if (can_drive == 'True' and candrive_endtime < time.time()) or (is_driving == 'True' and drive_endtime < time.time()):
                    # they've waited too long. YEET
                    print("User {} at {} waited too long to start driving!".format(next_user, next_user_IP))
                    db_conn.cursor().execute("DELETE FROM users WHERE user_name = ? and IP_addr = ?", (user_name, IP_addr))
                    db_conn.commit()
                    session.clear()
                    return redirect(url_for("index"))

                elif is_driving == 'True' and drive_endtime >= time.time():
                    # no need to update DB here, user should already be driving.
                    print("User {} at {} should be driving with {} s left!!".format(user_name, IP_addr, drive_endtime - int(time.time())))

                else: # update their status to "driving"
                    end_time = int(time.time()) + drive_timeout
                    db_conn.cursor().execute("UPDATE users SET can_drive='False', is_driving='True', drive_endtime=? WHERE rowid = (SELECT min(rowid) FROM users);", (end_time, ))
                    db_conn.commit()
                    print("User {} at {} can now drive with {} s left!!".format(user_name, IP_addr, end_time - int(time.time())))
                return render_template("drive.html", user=user_name)
            except:
                print("'is_driving': {}, and type is {}".format(is_driving, type(is_driving)))
                return render_template("drive.html", user=user_name)

        except (AssertionError, TypeError):
            print("Directing user to wait, it's not their dang turn!!")
            return redirect(url_for("wait"))

    @app.route("/check_turn")
    def check_turn():
        """ Called from the wait.html page, this function checks whether to display
            the DRIVE button for a user.
        """
        try:
            # try to remove that user from the DB
            user_name = session["user_name"]
            IP_addr = session["IP_addr"]
            print("Checking if it's {} from IP {}'s turn".format(user_name, IP_addr))
            db_conn = create_connection(database)
            # first assert that we were actually the next user, just in case
            try:
                # first, make sure user even exists
                db_conn.cursor().execute("SELECT * FROM users WHERE user_name=? AND ip_addr=?", (user_name, IP_addr)).fetchone()[0]
            except:
                # this user doesn't even exist in our database...
                session.clear()
                return jsonify(dict(redirect='/'))
            (next_user, next_user_IP, can_drive, is_driving, candrive_endtime, drive_endtime) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
            print("next_user: {}, next_user_IP: {}, can_drive: {}, candrive_endtime: {}".format(next_user, next_user_IP, can_drive, candrive_endtime))
            # if is_driving == "False" and can_drive == "False":
            #     # we know that this user is next since they're not driving and have not been selected to drive.
            #     print("User {} at IP {} can now drive.".format(next_user, next_user_IP))
            #     db_conn.cursor().execute("UPDATE users SET can_drive='True', can_drive_endtime=? WHERE rowid = (SELECT min(rowid) FROM users);", (int(time.time()) + wait_timeout, ))
            #     db_conn.commit()
            #     return jsonify(is_it_my_turn = "True")
            if can_drive == "True" and candrive_endtime >= time.time() and next_user == user_name:
                print("It is in fact {} from IP {}'s turn!!!".format(user_name, IP_addr))
                return jsonify(is_it_my_turn = "True", end_time=candrive_endtime)
            elif (can_drive == "True" and candrive_endtime < time.time()):
                print("user {} waited or took too long too drive, and their turn is over. YEET".format(user_name))
                db_conn.cursor().execute("DELETE FROM users WHERE user_name = ? and IP_addr = ?", (user_name, IP_addr))
                db_conn.commit()
                session.clear()
                # try to grab next eligible user and set their ability to drive
                try:
                    (next_user, next_user_IP, _, _, _, _) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
                    # finally, update the time by which the next user must start driving for the next user
                    db_conn.cursor().execute("UPDATE users SET can_drive='True', can_drive_endtime=? WHERE rowid = (SELECT min(rowid) FROM users);", (int(time.time()) + wait_timeout, ))
                    db_conn.commit()
                    print("Set user {} at {}'s can_drive_endtime to {}".format(next_user, next_user_IP, can_drive_endtime))
                except:
                    # there is no next user.
                    pass
                return jsonify(dict(redirect='/'))
            else:
                print("User {} from IP {} is still waiting".format(user_name, IP_addr))
                return jsonify(is_it_my_turn = "False")

        except (KeyError, AssertionError):
            pass
        # if we're not next, or there's no session key, return false
        return jsonify(is_it_my_turn = "False")


    @app.route("/driver_timeout")
    def driver_timeout():
        try:
            # try to remove that user from the DB
            user_name = session["user_name"]
            IP_addr = session["IP_addr"]
            print("Deleting {} from IP {} from DB".format(user_name, IP_addr))
            db_conn = create_connection(database)
            # delete this user from the DB
            db_conn.cursor().execute("DELETE FROM users WHERE user_name = ? and IP_addr = ?", (user_name, IP_addr))
            db_conn.commit()

            # stop all outputs
            if not DEV:
                GPIO.output(IN1, GPIO.LOW)
                GPIO.output(IN2, GPIO.LOW)
                GPIO.output(IN3, GPIO.LOW)
                GPIO.output(IN4, GPIO.LOW)

            try:
                (next_user, next_user_IP, _, _, _, _) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
                # finally, update the time by which the next user must start driving for the next user
                print("driver_timeout: trying to update user entry")
                db_conn.cursor().execute("UPDATE users SET can_drive='True', can_drive_endtime=? WHERE rowid = (SELECT min(rowid) FROM users);", (int(time.time()) + wait_timeout, ))
                db_conn.commit()
                print("Set user {} at {}'s can_drive_endtime to {}".format(next_user, next_user_IP, can_drive_endtime))
            except:
                # there is no next user.
                print("driver_timeout: could not update user entry.")
                pass

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
            names = [user_name[0] for user_name in user_names] # each entry is actually "('name',)"
            return render_template("wait.html", user_name=user_name, user_names=names)
        else:
            return render_template("wait.html", user_name=None, user_names=None)

    @app.route("/user_wait_timeout")
    def user_wait_timeout():
        """ This function is called when the user has waited past their alloted time to take controls
        of the tank, from the wait page.
        """
        try:
            user_name = session["user_name"]
            IP_addr = session["IP_addr"]
        except KeyError:
            print("Wait: Could not find user_name in session.")
            return "nothing"

        # grab next user currently waiting (should be the user calling this function)
        db_conn = create_connection(database)
        (next_user, next_user_IP, can_drive, _, can_drive_endtime, _) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()

        if can_drive == "True" and can_drive_endtime < time.time():
            # just make sure we got the right user.
            print("User {} at IP {} did not take control of the tank in time!!".format(user_name, IP_addr))
            db_conn.cursor().execute("DELETE FROM users WHERE user_name = ? and IP_addr = ?", (user_name, IP_addr))
            db_conn.commit()
            # clear session data and redirect to the wait page
            session.clear()
        # either way, return them to the wait page.
        return jsonify(dict(redirect='/wait'))

    @app.route('/left_start')
    def left_start():
        db_conn = create_connection(database)
        try:
            user_name = session["user_name"]
            IP_addr = session["IP_addr"]
            (next_user, next_user_IP, _, _, _, _) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
            assert user_name == next_user
            assert next_user_IP == IP_addr
            print("User {} started turning left".format(user_name))

            if not DEV:
                GPIO.output(IN1, GPIO.LOW)
                GPIO.output(IN2, GPIO.HIGH)
                GPIO.output(IN3, GPIO.HIGH)
                GPIO.output(IN4, GPIO.LOW)
                pwm_ENA.ChangeDutyCycle(50)
                pwm_ENB.ChangeDutyCycle(50)
        except:
            print("non-registered user has requested to start")
        # javascript requires a return statement
        return "Success"

    @app.route('/stop')
    def stop():
        db_conn = create_connection(database)
        try:
            user_name = session["user_name"]
            IP_addr = session["IP_addr"]
            (next_user, next_user_IP, _, _, _, _) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
            assert user_name == next_user
            assert next_user_IP == IP_addr
            print("User {} stopped moving".format(user_name))
            if not DEV:
                GPIO.output(IN1, GPIO.LOW)
                GPIO.output(IN2, GPIO.LOW)
                GPIO.output(IN3, GPIO.LOW)
                GPIO.output(IN4, GPIO.LOW)
        except:
            print("non-registered user has requested to stop")

        return "Success"

    @app.route('/right_start')
    def right_start():
        db_conn = create_connection(database)
        try:
            user_name = session["user_name"]
            IP_addr = session["IP_addr"]
            (next_user, next_user_IP, _, _, _, _) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
            assert user_name == next_user
            assert next_user_IP == IP_addr
            print("User {} started turning right".format(user_name))
            if not DEV:
                GPIO.output(IN1, GPIO.HIGH)
                GPIO.output(IN2, GPIO.LOW)
                GPIO.output(IN3, GPIO.LOW)
                GPIO.output(IN4, GPIO.HIGH)
                pwm_ENA.ChangeDutyCycle(50)
                pwm_ENB.ChangeDutyCycle(50)
        except:
            print("non-registered user has requested to start")
        # javascript requires a return statement
        return "Success"

    @app.route('/forward_start')
    def forward_start():
        db_conn = create_connection(database)
        try:
            user_name = session["user_name"]
            IP_addr = session["IP_addr"]
            (next_user, next_user_IP, _, _, _, _) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
            assert user_name == next_user
            assert next_user_IP == IP_addr
            print("User {} started going forward".format(user_name))
            if not DEV:
                GPIO.output(IN1, GPIO.HIGH)
                GPIO.output(IN2, GPIO.LOW)
                GPIO.output(IN3, GPIO.HIGH)
                GPIO.output(IN4, GPIO.LOW)
                pwm_ENA.ChangeDutyCycle(50)
                pwm_ENB.ChangeDutyCycle(50)
        except:
            print("non-registered user has requested to start")
        # javascript requires a return statement
        return "Success"

    @app.route('/reverse_start')
    def reverse_start():
        db_conn = create_connection(database)
        try:
            user_name = session["user_name"]
            IP_addr = session["IP_addr"]
            (next_user, next_user_IP, _, _, _, _) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
            assert user_name == next_user
            assert next_user_IP == IP_addr
            print("User {} started reversing".format(user_name))
            if not DEV:
                GPIO.output(IN1, GPIO.LOW)
                GPIO.output(IN2, GPIO.HIGH)
                GPIO.output(IN3, GPIO.LOW)
                GPIO.output(IN4, GPIO.HIGH)
                pwm_ENA.ChangeDutyCycle(50)
                pwm_ENB.ChangeDutyCycle(50)
        except:
            print("non-registered user has requested to start")
        # javascript requires a return statement
        return "Success"

    @app.route('/shot_start')
    def shot_start():
        db_conn = create_connection(database)
        try:
            user_name = session["user_name"]
            IP_addr = session["IP_addr"]
            (next_user, next_user_IP, _, _, _, _) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
            assert user_name == next_user
            assert next_user_IP == IP_addr
            print("User {} poured a shot!".format(user_name))
            if not DEV:
                t = threading.Thread(target=shot.pour_shot, args=())
                t.start()

        except:
            print("non-registered user has requested to pour shot")
        # javascript requires a return statement
        return "Success"

    @app.route('/camera')
    def camera():
        db_conn = create_connection(database)
        try:
            user_name = session["user_name"]
            IP_addr = session["IP_addr"]
            (next_user, next_user_IP, _, _, _, _) = db_conn.cursor().execute("SELECT * FROM users WHERE rowid = (SELECT min(rowid) FROM users);").fetchone()
            assert user_name == next_user
            assert next_user_IP == IP_addr
            print("User {} took a picture!".format(user_name))
            if not DEV:
                t = threading.Thread(target=os.system('uvccapture -v -m'), args=())
                t.start()

        except:
            print("non-registered user has requested to take picture")
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
