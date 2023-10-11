import yukinator
import pandas as pd
import numpy as np
import datetime
import re
import requests

YEAR = datetime.datetime.now().year
y = yukinator.Yuki()


def get_current_season_completed_race():
    """get number of races completed for current season"""
    is_current = False
    current_drivers_standings = y.get_drivers_standings(year=YEAR)
    race = 0
    all_drivers_standings = []

    while not is_current:
        race += 1
        drivers_standings_single_race = y.get_drivers_standings(year=YEAR, race=race)
        drivers_standings_single_race_df = pd.DataFrame(
            [
                driver_standing.to_flat_dict()
                for driver_standing in drivers_standings_single_race
            ]
        )
        all_drivers_standings.append(drivers_standings_single_race_df)
        is_current = drivers_standings_single_race == current_drivers_standings

    all_drivers_standings_df = pd.concat(
        [df.assign(race=i + 1) for i, df in enumerate(all_drivers_standings)],
        ignore_index=True,
    )
    return (race, all_drivers_standings_df)


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


def map_driver_team(df, driver_info):
    """get favorite driver"""
    driver_and_team = df[["driverCode", "constructor"]].drop_duplicates()
    driver_to_team = dict(
        zip(driver_and_team["driverCode"], driver_and_team["constructor"])
    )
    team_to_driver = dict()
    for key, value in driver_to_team.items():
        if value in team_to_driver.keys():
            team_to_driver[value].append(key)
        else:
            team_to_driver[value] = [key]
    driver_info["contructor"] = driver_info["code"].apply(lambda x: driver_to_team[x])
    driver_team_info = driver_info.set_index("code").to_dict(orient="index")
    return (team_to_driver, driver_team_info)
