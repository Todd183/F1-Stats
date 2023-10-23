# F1-Stats
A F1 statistics website built with python Flask. 

# User Guide

## 1. Setting Up the Environment

Before running the program, ensure that you have Python 3.10 installed. To set up the necessary dependencies, navigate to the project directory and run "pip install -r requirements.txt"

## 2. Running the Program

navigate to the project directory and execute "main.py"

## 3. Accessing the Website

Open your web browser and enter "http://127.0.0.1:8000."

## 4. Signing Up

To create an account, provide the following information:

- Email address (minimum 4 characters)
- User name (minimum 2 characters)
- Password (minimum 7 characters)
- Select your favorite F1 team from the following options:
  - Red Bull
  - Aston Martin
  - Ferrari
  - Mercedes
  - Alfa Romeo
  - Alpine F1 Team
  - Williams
  - AlphaTauri
  - Haas F1 Team
  - McLaren

**Please Note**: The first-time sign-up process takes approximately one minute to fetch and build the F1 database for the current season. 

## 5. Logging In

Log in with your account credentials.

## 6. Exploring the Website

Upon logging in, the website will redirect you to the home page, where you can view your favorite team, both drivers' statistics, dynamic performance trends, and the schedule for the next Grand Prix in the New Zealand time zone.

## 7. Navigation Bar Options

In the navigation bar, you can click "Points" to view dynamic points trends for all drivers or click "Positions" to view dynamic positions trends for all drivers.

## 8. Project file structure

```bash
.
├── README.md #git hub Readme file
├── main.py # main python file to excute
├── requirements.txt # python libraries dependencies records
└── website
    ├── __init__.py # initiate the website after runing main.py
    ├── auth.py # backend codes for login, log out and sign up page
    ├── get_F1_data.py # define customized functions that get and process F1 data
    ├── models.py # define data class for database
    ├── static
    │   ├── data
    │   │   └── schedule.json #race schedule data
    │   ├── index.js
    │   └── team_logo #team pictures file
    │       ├── Alfa Romeo.png
    │       ├── AlphaTauri.png
    │       ├── Alpine F1 Team.png
    │       ├── Aston Martin.png
    │       ├── Ferrari.png
    │       ├── Haas F1 Team.png
    │       ├── McLaren.png
    │       ├── Mercedes.png
    │       ├── Red Bull.png
    │       └── Williams.png
    ├── templates
    │   ├── base.html #base template html file
    │   ├── home.html #home page
    │   ├── login.html #login page
    │   ├── logout.html #logout page
    │   ├── points.html #points page
    │   ├── positions.html #positions page
    │   └── sign_up.html #sign up page
    └── views.py # backend codes for home, points, and positions page
```
