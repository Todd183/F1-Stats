import yukinator
import pandas as pd
import numpy as np
import datetime
import re
import requests
import json
import pytz

YEAR = datetime.datetime.now().year
y = yukinator.Yuki()


def get_races():
    """get races for current seasons"""
    races = pd.DataFrame([race.to_flat_dict() for race in y.get_races(year=YEAR)])
    races["datetime"] = pd.to_datetime(
        races["date"].astype(str) + " " + races["time"].astype(str)
    )
    new_zealand_timezone = pytz.timezone("Pacific/Auckland")
    races["datetime"] = races["datetime"].dt.tz_convert(new_zealand_timezone)
    races["nz_date"] = races["datetime"].dt.date
    races["nz_time"] = races["datetime"].dt.time
    races["nz_time"] = pd.to_datetime(races["nz_time"], format="%H:%M:%S").dt.strftime(
        "%I:%M %p"
    )
    return races


# def get_schedule():
#     """get shedule"""
#     json_file_path = "./website/static/data/schedule.json"
#     with open(json_file_path, "r") as json_file:
#         data = json.load(json_file)
#     schedule = pd.DataFrame(data)
#     schedule["Date"] = schedule["Date"].apply(
#         lambda x: datetime.datetime.strptime(x, "%B %d %Y").strftime("%Y-%m-%d")
#     )
#     schedule["Date"] = pd.to_datetime(schedule["Date"])
#     return schedule


def get_current_season_completed_race():
    """get number of races completed for current season"""
    # is_current = False
    # current_drivers_standings = y.get_drivers_standings(year=YEAR)
    # race = 0

    all_drivers_standings = []
    current_date = pd.to_datetime(datetime.datetime.now().date()) - datetime.timedelta(
        days=1
    )
    races = get_races()
    rounds = sum((pd.to_datetime(races["date"]) < current_date).to_list())
    for round in range(
        1,
        rounds + 1,
    ):
        drivers_standings_single_race = y.get_drivers_standings(year=YEAR, race=round)
        drivers_standings_single_race_df = pd.DataFrame(
            [
                driver_standing.to_flat_dict()
                for driver_standing in drivers_standings_single_race
            ]
        )
        all_drivers_standings.append(drivers_standings_single_race_df)

    all_drivers_standings_df = pd.concat(
        [df.assign(race=i + 1) for i, df in enumerate(all_drivers_standings)],
        ignore_index=True,
    )
    return (rounds, all_drivers_standings_df)


def clean_df(all_drivers_standings_df):
    """clean all_drivers_standings_df"""
    all_drivers_standings_df["constructor"] = all_drivers_standings_df[
        "Constructors"
    ].apply(lambda x: x[0]["name"])

    driver_to_construtor = all_drivers_standings_df[
        ["driverCode", "constructor"]
    ].drop_duplicates()

    wide_df = all_drivers_standings_df.pipe(
        lambda x: x[["driverCode", "points", "race"]]
    ).pivot(index="race", columns="driverCode", values="points")
    wide_df.iloc[0] = wide_df.iloc[0].replace(np.nan, 0)
    wide_df.fillna(method="ffill", inplace=True)
    df = wide_df.stack().reset_index()
    df.columns = ["race", "driverCode", "points"]
    df["positions"] = (
        df.groupby("race")["points"]
        .rank(ascending=False, method="min")  # driver ranking
        .astype(int)
    )
    df = df.merge(driver_to_construtor, on="driverCode", how="left")
    return df


def getPlotData(clean_all_drivers_standings_df):
    """get plot Data"""
    ctors = clean_all_drivers_standings_df["constructor"].drop_duplicates().tolist()
    colors = [
        "#0073C2FF",
        "#EFC000FF",
        "#868686FF",
        "#CD534CFF",
        "#7AA6DCFF",
        "#003C67FF",
        "#8F7700FF",
        "#3B3B3BFF",
        "#A73030FF",
        "#4A6990FF",
    ]
    ctors_to_color = pd.DataFrame({"constructor": ctors, "color": colors})
    temp_df = clean_all_drivers_standings_df.merge(
        ctors_to_color, on="constructor", how="left"
    )
    plotdata = [temp_df.columns.tolist()]
    plotdata.extend(temp_df.values.tolist())
    return plotdata


def getdata():
    """get and clean F1 race data"""
    current_race, all_drivers_standings_df = get_current_season_completed_race()
    clean_all_drivers_standings_df = clean_df(all_drivers_standings_df)
    return (current_race, clean_all_drivers_standings_df)


def get_wikipedia_main_pic_url(article_title):
    endpoint = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "format": "json",
        "titles": article_title,
        "prop": "pageimages",
        "pithumbsize": 300,  # Adjust the thumbnail size as needed
    }

    response = requests.get(endpoint, params=params)
    data = response.json()

    page_id = list(data["query"]["pages"].keys())[0]
    main_image_url = data["query"]["pages"][page_id]["thumbnail"]["source"]

    return main_image_url


def try_get_wikipedia_main_pic_url(x):
    try:
        result = get_wikipedia_main_pic_url(x)
    except Exception as e:
        # Handle the exception (e.g., print an error message)
        print(f"Error processing {x}: {e}")
        result = None

    return result


def get_driver_info():
    drivers = pd.DataFrame(
        [driver.to_flat_dict() for driver in y.get_drivers(year=YEAR)]
    )
    # Define the regex pattern to match the input text
    pattern = r"http://en.wikipedia.org/wiki/"
    # Define the replacement text with the modified URL
    replacement = r""
    drivers["article_title"] = drivers["url"].apply(
        lambda x: re.sub(pattern, replacement, x)
    )

    # manual modification of wiki article_titles
    conditions = [
        drivers["article_title"] == "Alexander_Albon",
        drivers["article_title"] == "Nico_H%C3%BClkenberg",
        drivers["article_title"] == "Sergio_P%C3%A9rez",
    ]
    values = ["Alex_Albon", "Nico_Hülkenberg", "Sergio_Pérez"]
    drivers["article_title"] = np.select(
        conditions, values, default=drivers["article_title"]
    )
    # url_dict = dict([(driver_code, (try_get_wikipedia_main_pic_url(driver_article_title))) for driver_code, driver_article_title in dict(zip(drivers["code"],drivers["article_title"])).items()])

    # url_df = pd.DataFrame(code = list(url_dict.keys(), pic_url = list(url_dict.values())))

    drivers["pic_url"] = drivers["article_title"].apply(
        lambda x: try_get_wikipedia_main_pic_url(x)
    )

    return drivers


def get_complete_driver_info(df, driver_info):
    """get favorite driver"""
    current_drivers = (
        df[df["race"] == df["race"].max()]
        .set_index("driverCode")
        .to_dict(orient="index")
    )
    drivers = driver_info.set_index("code").to_dict(orient="index")
    for key in current_drivers.keys():
        drivers[key].update(current_drivers[key])
    return drivers


def get_team_to_driver(df):
    driver_to_team = (
        df[["driverCode", "constructor"]]
        .drop_duplicates()
        .set_index("driverCode")
        .to_dict(orient="index")
    )
    team_to_driver = dict()
    for key in driver_to_team.keys():
        value = driver_to_team[key]["constructor"]
        if value in team_to_driver.keys():
            team_to_driver[value].append(key)
        else:
            team_to_driver[value] = [key]
    return team_to_driver


def get_profile(drivers):
    """build driver profile for front-end"""
    profile_items = [
        "givenName",
        "familyName",
        "dateOfBirth",
        "nationality",
        "permanentNumber",
        "contructor",
        "points",
        "positions",
        "constructo",
    ]
    profile = dict()
    for key1, value1 in drivers.items():
        profile[key1] = dict()
        # temp = {"profile": {key2: value2} for key2, value2 in value1.items() if key2 in profile_items }
        [(key2, value2) for key2, value2 in value1.items() if key2 in profile_items]
        profile[key1]["profile"] = dict(
            [(key2, value2) for key2, value2 in value1.items() if key2 in profile_items]
        )
        for key2, value2 in value1.items():
            if key2 not in profile_items:
                profile[key1][key2] = value2
    return profile


def is_uptodate(df, races):
    """check uptodate"""
    current_date = pd.to_datetime(datetime.datetime.now().date())
    num_of_races = sum((pd.to_datetime(races["nz_date"]) < current_date).to_list())
    return df["race"].max() + 1 >= num_of_races


def get_next_race(races):
    """get next races"""
    current_date = pd.to_datetime(datetime.datetime.now().date())
    races_not_completed = (pd.to_datetime(races["nz_date"]) > current_date).to_list()
    is_season_finished = sum(races_not_completed) == 0
    if not is_season_finished:
        next_race = races[races_not_completed].iloc[[0]].to_dict(orient="records")
    else:
        next_race = "Current Season finished!"
    return (is_season_finished, next_race)
