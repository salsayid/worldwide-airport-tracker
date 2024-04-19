# Milestone 1 Package Deal Tracker App
Made by Nathaniel McVay

## Project Components
This project consists of two main components:

### Tracking App
The tracking app is implemented in `main.py` as `PackageDealApp`. This app allows you to manage venues and operators, and check forecasts.

### Installer
The installer is implemented in `installer.py`. This script sets up the database for the tracking app.

## Status
The tracking app is mostly complete, but there are still some areas that need work:
- The `CheckForecastScreen` class in `main.py` is currently being worked on.

## Building and Running the Apps

### Dependencies
This project requires the following Python libraries:
- Kivy
- SQLAlchemy

You can install these dependencies using pip:
- pip install kivy
- pip install sqlalchemy


### Building
No build step is required as this is a Python project.


### Database Creation
The installer script `installer.py` will automatically create the necessary database tables when run. It uses the settings defined in `credentials.py` to connect to the database.
You will need to create a database beforehand and put those credentials into `credentials.py`.


### Running
To run the tracking app, import the project into your IDE of choice and create a new .py file titled `credentials.py`
and with the information according to the instructions in the example file, `credentials_example.py`. Then run `installer.py` which will set up the
tables in your database. After that point run `main.py` and enjoy the Package Deal Tracker App.