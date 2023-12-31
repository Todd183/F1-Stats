from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from .get_F1_data import getdata, get_driver_info, get_races


auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    """define login in page"""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # handle unsuccessful login
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect password, try again.", category="error")
        else:
            flash("Email does not exist.", category="error")

    return render_template("login.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    """redirect to login page after logout"""
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    """define sign up page"""

    if request.method == "POST":
        email = request.form.get("email")
        usr_name = request.form.get("usr_name")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        constructor = request.form.get("constructor")

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists.", category="error")
        elif len(email) < 4:
            flash("Email must be greater than 4 characters.", category="error")
        elif len(usr_name) < 2:
            flash("User Name must be at least 2 characters.", category="error")
        elif password1 != password2:
            flash("Passwords don't match", category="error")
        elif len(password1) < 7:
            flash("Passwords must be at least 7 characters.", category="error")
        else:
            # add user to the data base

            current_race, df = getdata()
            driver_info = get_driver_info()
            races = get_races()

            new_user = User(
                email=email,
                usr_name=usr_name,
                password=generate_password_hash(password1, method="sha256"),
                constructor=constructor,
                current_race=current_race,
            )
            db.session.add(new_user)

            races.to_sql(
                name="current_races_F1", con=db.engine, index=False, if_exists="replace"
            )

            df.to_sql(
                name="current_results_F1",
                con=db.engine,
                index=False,
                if_exists="replace",
            )
            driver_info.to_sql(
                name="driver_info_F1", con=db.engine, index=False, if_exists="replace"
            )

            db.session.commit()

            flash("Account created", category="success")
            return redirect(url_for("auth.login"))

    return render_template("sign_up.html", user=current_user)
