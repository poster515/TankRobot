from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from datetime import datetime

from helpers import apology, login_required, lookup, usd
import string

# Configure application
app = Flask(__name__)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    if not session["user_id"]:
        return redirect("/login")

    else:
        index_info = []

        stock_total = 0

        user_stock_info = db.execute("SELECT * FROM user_stocks where user_id = :user_id", user_id = session["user_id"])

        for row in user_stock_info:
            # get stock info for result set row
            stock_info = lookup(row["symbol"])

            # now get the total current worth of the users stocks
            stock_value = row["numshares"] * stock_info["price"]

            # get total stock net worth
            stock_total = stock_total + stock_value

            # # append all this data in an object to pass to index.html
            index_info.append([stock_info["symbol"], stock_info["name"], row["numshares"], usd(stock_info["price"]), usd(stock_total)])

        row = db.execute("SELECT cash FROM users where id = :user_id", user_id=session["user_id"])

        return render_template("index.html", cash=usd(row[0]["cash"]), total=usd(row[0]["cash"] + stock_total), index_info=index_info)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("Please enter a stock symbol to buy")

        symbol = request.form.get("symbol")

        try:
            shares = int(request.form.get("shares"))
            if shares < 0:  # if not a positive int print message and ask for input again
                return apology("Shares must be a positive integer")

        except ValueError:
            return apology("Shares must be a positive integer")

        # check if stock symbol is valid:
        info = lookup(symbol)

        # check if user has enough cash:
        if info:
            cash = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])
            netcash = cash[0]["cash"] - (shares * info["price"])

        else: #if info doesn't exist, then the stock symbol was bad
            return apology("Stock doesn't exist or is not formatted correctly")

        if netcash < 0:
            # user does not have enough money to purchase
            return apology("You do not have enough money for this transaction")

        else:
            # log this transaction into table
            # bought/sold, symbol, purchase/sale price, number of shares, datetime

            db.execute("INSERT into transactions (user_id, type, symbol, price, numshares, datetime) VALUES (:user_id, :type, :symbol, :price, :numshares, :datetime)",
                user_id=session["user_id"],
                type="BUY",
                symbol=symbol,
                price=info["price"],
                numshares=shares,
                datetime=datetime.now())

            # update users cash in 'users'
            db.execute("UPDATE users SET cash = :cash WHERE id = :id", cash = netcash, id = session["user_id"])

            # update 'user_stocks' with new stock info
            row=db.execute("SELECT * FROM user_stocks where (user_id = :user_id) AND (symbol = :symbol)", user_id=session["user_id"], symbol=symbol)

            if not row:
                db.execute("INSERT into user_stocks (user_id, symbol, numshares, bought_price) VALUES (:user_id, :symbol, :numshares, :bought_price)",
                    user_id=session["user_id"],
                    symbol=symbol,
                    numshares=shares,
                    bought_price=info["price"])

            else:
                bought_price = row["bought_price"] + (shares * info["price"])

                shares = row["numshares"] + shares

                db.execute("UPDATE user_stocks set (numshares=:numshares) and (bought_price=:bought_price) where (user_id = :user_id) and (symbol = :symbol)",
                    numshares=shares,
                    bought_price=bought_price,
                    user_id=session["user_id"],
                    symbol=symbol)

            return redirect("/")
    else:
        return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    rows = db.execute("SELECT * FROM transactions where user_id=:user_id", user_id=session["user_id"])

    user_history = []

    for row in rows:
        user_history.append([row["type"], row["symbol"], row["price"], row["numshares"], row["datetime"]])
    return render_template("history.html", user_history=user_history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        # "lookup" method return type: name (as a str), price (as a float), and (uppercased) symbol (as a str)

        # return {
        #     "name": row[1],
        #     "price": price,
        #     "symbol": row[0].upper()
        # }

        if not symbol:
            return apology("Must enter stock symbol")

        info = lookup(symbol)

        if info == None:
            return apology("Stock doesn't exist or is not formatted correctly")

        else:
            info["price"] = usd(info["price"])
            return render_template("quoted.html", info=info)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        user = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            return apology("Not enough information provided")

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords do not match")

        elif not user:
            for char in string.punctuation:
                if char in request.form.get("password"):
                    for num in string.digits:
                        if num in request.form.get("password"):
                            user = db.execute("INSERT into users (username, hash) VALUES (:username, :hash)",
                                username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")))

                            return render_template("login.html")
            return apology ("Password must contain at least one special character and one number")
        else:
            return apology("Username already exists.")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":

        try:
            shares = int(request.form.get("shares"))
            if shares < 1:  # if not a positive int print message and ask for input again
                return apology("Shares must be a positive integer")

        except ValueError:
            return apology("Shares must be a positive non-zero integer")

        symbol = request.form.get("symbol")

        row = db.execute("SELECT * FROM user_stocks WHERE (user_id = :user_id) AND (symbol = :symbol)", user_id=session["user_id"], symbol=symbol)

        if not symbol:
            return apology("Must select a stock to sell")

        elif not row:
            return apology("You do not own this stock")

        elif row[0]["numshares"] < shares:
            return apology("You do not have that many shares")

        else:
            info = lookup(symbol)
            if info != None:

                netshares = row[0]["numshares"] - shares

                user = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])

                netcash = user[0]["cash"] + (info["price"] * shares)

                db.execute("UPDATE users set cash=:netcash where id=:user_id", netcash=netcash, user_id=session["user_id"])

                if netshares > 0:
                    db.execute("UPDATE user_stocks set numshares=:netshares where (user_id=:user_id) and (symbol=:symbol)",
                        netshares=netshares,
                        user_id=session["user_id"],
                        symbol=symbol)

                else:
                    db.execute("DELETE FROM user_stocks WHERE (user_id=:user_id) and (symbol=:symbol)",
                        user_id=session["user_id"],
                        symbol=symbol)

                # log this transaction into table
                db.execute("INSERT into transactions (user_id, type, symbol, price, numshares, datetime) VALUES (:user_id, :type, :symbol, :price, :numshares, :datetime)",
                    user_id=session["user_id"],
                    type="SELL",
                    symbol=symbol,
                    price=info["price"],
                    numshares=shares,
                    datetime=datetime.now())

                return redirect("/")
            else:
                return apology("Stock selected is not valid")
    else:
        symbols = []

        user_stock_info = db.execute("SELECT * FROM user_stocks where user_id = :user_id", user_id = session["user_id"])

        for row in user_stock_info:
            # append all this data in an object to pass to sell.html
            symbols.append(row["symbol"])

        return render_template("sell.html", symbols=symbols)



def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)