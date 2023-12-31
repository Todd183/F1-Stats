from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import User
from website import db
from .get_F1_data import (
    getPlotData,
    get_complete_driver_info,
    get_team_to_driver,
    get_profile,
    is_uptodate,
    get_next_race,
    getdata,
)

import datetime
import pandas as pd


views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
@login_required
def home():
    """get and pass data to frontend before loading home page"""

    df_sql_query = "SELECT * FROM current_results_F1"
    df = pd.read_sql_query(df_sql_query, db.engine)

    races_sql_query = "SELECT * FROM current_races_F1"
    races = pd.read_sql_query(races_sql_query, db.engine)

    # check whether data is up-to-date before loading home page
    # If database is not up to date then update database first
    if not is_uptodate(df, races):
        current_race, df = getdata()
        df.to_sql(
            name="current_data_F1", con=db.engine, index=False, if_exists="replace"
        )
        db.session.commit()

    is_season_finished, next_race = get_next_race(races)
    plotdata = getPlotData(df)
    team_to_driver = get_team_to_driver(df)

    driver_sql_query = "SELECT * FROM driver_info_F1"
    driver_info = pd.read_sql_query(driver_sql_query, db.engine)

    drivers = get_complete_driver_info(df, driver_info)
    profiles = get_profile(drivers)

    favorite_drivers = team_to_driver[current_user.constructor]

    current_year = datetime.datetime.now().date().year
    return render_template(
        "home.html",
        user=current_user,
        plotdata=plotdata,
        team_to_driver=team_to_driver,
        drivers=drivers,
        favorite_drivers=favorite_drivers,
        profiles=profiles,
        is_season_finished=is_season_finished,
        next_race=next_race,
        current_year=current_year,
    )


@views.route("/positions", methods=["GET", "POST"])
@login_required
def positions():
    """get and pass data to frontend before loading positions page"""

    df_sql_query = "SELECT * FROM current_results_F1"
    df = pd.read_sql_query(df_sql_query, db.engine)
    current_year = datetime.datetime.now().date().year

    plotdata = getPlotData(df)
    drivers = list(set([i[1] for i in plotdata[1:]]))
    return render_template(
        "positions.html",
        user=current_user,
        plotdata=plotdata,
        current_year=current_year,
        drivers=drivers,
    )


@views.route("/points", methods=["GET", "POST"])
@login_required
def points():
    """get and pass data to frontend before loading points page"""

    df_sql_query = "SELECT * FROM current_results_F1"
    df = pd.read_sql_query(df_sql_query, db.engine)
    current_year = datetime.datetime.now().date().year

    plotdata = getPlotData(df)
    drivers = list(set([i[1] for i in plotdata[1:]]))
    return render_template(
        "points.html",
        user=current_user,
        plotdata=plotdata,
        current_year=current_year,
        drivers=drivers,
    )
