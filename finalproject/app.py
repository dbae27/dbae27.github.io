import os
import sqlite3

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

loggedin = False

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

@app.route("/")
def index():
    # Fetch the new_text from the session, or use a default value
    home_text = session.get("edited_text", ("Welcome to The Asian American Foundation's Youth Initiative. Together we can empower the next generation of AAPI."))

    return render_template("index.html", home_text = home_text)

@app.route("/about")
def about():
    # Fetch the new_text from the session, or use a default value
    about_text = session.get("new_text", (
        "Started in the Fall of 2023 by Harvard freshman Daniel Bae, "
        "the TAAF AAPI Youth Initiative seeks to expand The Asian American Foundation's "
        "efforts to reach college campuses. With the help of 2 friends, Aaron Joy and "
        "Vincent Lo, Bae has begun partnerships with 5 campus groups at Harvard - "
        "the initiative is just getting started!"
    ))

    return render_template("about.html", about_text=about_text)

from flask import render_template

@app.route("/events")
def events():
    events = db.execute('SELECT title, description, image FROM events')
    return render_template("events.html", events = events)

@app.route("/partners")
def partners():

    # Fetch partners from the database
    partners = db.execute('SELECT name, website, School FROM partnerinfo')

    # Fetch unique schools from the database
    unique_schools = db.execute("SELECT DISTINCT School FROM partnerinfo")
    print(unique_schools)

    # Extract school names as a list of strings
    unique_schools = [school["School"] for school in unique_schools]

    return render_template('partners.html', partners=partners, unique_schools=unique_schools)


@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    # Log user in, forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        elif request.form.get("username") != "TAAFY":
            return apology("invalid username")

        elif request.form.get("password") != "Jlin7177":
            return apology("invalid password")

        # Store the login status in the session
        session["user_id"] = "TAAFY"

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    # Clear the user's session
    session.clear()

    # Redirect user to the home page
    return redirect("/")


@app.route("/edit-about", methods=["GET", "POST"])
@login_required
def editabout():
    if request.method == "POST":
        new_about_text = request.form.get("new_text")

        if not new_about_text:
            return apology("About text cannot be empty", 400)

        # Save the updated about text to a variable, database, or any storage of your choice
        # For simplicity, let's assume you're saving it to a variable in the session
        session["new_text"] = new_about_text

        flash("About text updated successfully!")
        return redirect("/about")

    # Render the about page with the current about text
    return render_template("edit-about.html", new_text=session.get("new_text", "about_text"))

@app.route("/edit-home", methods=["GET", "POST"])
@login_required
def edithome():
    if request.method == "POST":
        new_home_text = request.form.get("new_text")

        if not new_home_text:
            return apology("Home text cannot be empty", 400)

        # Save the updated about text to a variable, database, or any storage of your choice
        # For simplicity, let's assume you're saving it to a variable in the session
        session["edited_text"] = new_home_text

        flash("Home text updated successfully!")
        return redirect("/")

    # Render the about page with the current about text
    return render_template("edit-home.html", new_text=session.get("edited_text", "home_text"))


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":

        if not request.form.get("name") or not request.form.get("website") or not request.form.get("School"):
            return apology("name, website, and school required", 400)

         # check if website exists
        websites = db.execute(
            "SELECT * FROM partnerinfo WHERE website = ?", request.form.get("website")
        )
        if len(websites) != 0:
            return apology("website already exists", 400)

        db.execute(
            "INSERT INTO partnerinfo (name, website, School) VALUES(?, ?, ?)",
            request.form.get("name"),
            request.form.get("website"),
            request.form.get("School")
         )

        return redirect("/partners")

    return render_template("add.html")


@app.route("/delete/<partner_name>", methods=["POST"])
@login_required
def delete_partner(partner_name):
    db.execute("DELETE FROM partnerinfo WHERE name = ?", partner_name)
    flash(f"Partner {partner_name} deleted successfully!")
    return redirect("/partners")

@app.route("/delete_event/<event_id>", methods = ["POST"])
@login_required
def delete_event(event_id):
    db.executve("DELTE FROM events WHERE id = ?", event_id)
    flash(f"Event {event_title} deleted successfully!")
    return redirect("/events")


@app.route("/confirm_delete/<partner_name>")
@login_required
def confirm_delete(partner_name):
    return render_template("confirm_delete.html", partner_name=partner_name)


if __name__ == "__main__":
    app.run(debug=True)
