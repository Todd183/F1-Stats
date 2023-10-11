from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, Transaction, User
from website import db
import json
from PIL import Image
from .get_F1_data import (
    getPlotData,
    get_complete_driver_info,
    get_team_to_driver,
    get_profile,
)

# import pytesseract
# import re
import pandas as pd

views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
@login_required
def home():
    df_sql_query = "SELECT * FROM current_data_F1"
    df = pd.read_sql_query(df_sql_query, db.engine)
    plotdata = getPlotData(df)
    team_to_driver = get_team_to_driver(df)

    driver_sql_query = "SELECT * FROM driver_info_F1"
    driver_info = pd.read_sql_query(driver_sql_query, db.engine)

    drivers = get_complete_driver_info(df, driver_info)
    profiles = get_profile(drivers)

    favorite_drivers = team_to_driver[current_user.constructor]

    xAxisData_new = [x[0] for x in df[["race"]].drop_duplicates().values]
    points = list(df["points"])
    positions = list(df["positions"])
    df_json = df.to_json()
    driver_and_team = df[["driverCode", "constructor"]].drop_duplicates()
    positions = df.pivot(
        index=["race"], columns="driverCode", values="positions"
    ).to_json()
    points = df.pivot(index=["race"], columns="driverCode", values="points").to_json()
    # drivers = list(set(df["driverCode"].tolist()))

    return render_template(
        "home.html",
        user=current_user,
        plotdata=plotdata,
        team_to_driver=team_to_driver,
        drivers=drivers,
        favorite_drivers=favorite_drivers,
        profiles=profiles
        # positions=positions,
        # points=points,
        # df=df_json,
        # driver_and_team=driver_and_team,
        # xAxisData_new=xAxisData_new,
        # drivers=drivers,
        # driver_info=driver_info,
    )


# @views.route("/scan_receipt", methods=["GET", "POST"])
# @login_required
# def scan_receipt():
#     if request.method == "POST":
#         uploaded_file = request.files["image"]
#         if uploaded_file.filename != "":
#             try:
#                 # Read the uploaded file as a stream
#                 file_stream = uploaded_file.read()
#                 # Create a BytesIO object and load the image from the stream
#                 image = Image.open(BytesIO(file_stream))
#                 # Perform OCR using pytesseract
#                 raw_text = pytesseract.image_to_string(image)
#                 # Regular expression to extract item names and prices (simplified example)
#                 pattern = (
#                     r"(\w+)\s+\$(\d+\.\d{2})"  # Assumes item name, space, price format
#                 )
#                 # Extract item names and prices using regex
#                 matches = re.findall(pattern, raw_text)
#                 # Create a list of dictionaries with item names and prices
#                 items = [
#                     {"name": match[0], "price": float(match[1])} for match in matches
#                 ]
#                 return text
#             except Exception as e:
#                 return str(e)

#     return render_template("scan_receipt.html", user=current_user)


@views.route("/note", methods=["GET", "POST"])
@login_required
def note():
    if request.method == "POST":
        note = request.form.get("note")

        if len(note) < 1:
            flash("Note is too short", category="error")
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash("Note added", category="success")

    return render_template("note.html", user=current_user)


@views.route("/delete-note", methods=["POST"])
def delete_note():
    note = json.loads(
        request.data
    )  # this function expects a JSON from the INDEX.js file
    noteId = note["noteId"]
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
