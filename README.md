
# Milestone 2: Travel Planner App



##### Authors:
Nathaniel McVay, Sayid Alsayid, Ethen Friedman, James Benton


## Project Components
This project consists of three main components:
### First Tracking App
The first tracking app is implemented in `package_main.py` as `PackageDealApp`. 
This app allows you to manage venues and operators, and check forecasts.
There is also an installer implemented in `installer.py`. this script
sets up the database for the tracking app.

### Second Tracking App
The second tracking app is implemented in `airport_main.py` as `AirportTrackerApp`. 
This app allows you to create new airports and cities, and check the forecasts as well.
The installer is implemented in `airport_installer.py`. This script sets up the database for the tracking app.

### Travel Planner App
The travel planner app is implemented in `travel_main.py` as `TravelPlannerApp`. This app 
allows you to enter an authority, port number, database name, username, and password for the remote database. 


## Status
The three main components are finished and complete. 

## Building and Running the Apps

### Dependencies

This project requires the following python libraries:
- Python 3.10 (or later)
- Kivy
- SQLAlchemy

You can install these dependencies using pip:

-`pip install kivy`

-`pip install sqlalchemy`

### Building

No build step is required as this is a Python project.

