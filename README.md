#Travel Planner App



##### Authors:

Lead Programmer - Sayid Alsayid

Contributions from - Ethan Friedman, James Benton, Nathaniel McVay


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
- Requests (for API calls)

You can install these dependencies using pip:

-`pip install kivy`

-`pip install sqlalchemy`

### Building

No build step is required as this is a Python project.

### Database Creation
The installer script `installer.py` will automatically create 
the necessary database tables when it is ran. It uses the 
settings defined in `credentials.py` to connect to the 
database. You will need to create a database beforehand 
and put those credentials into `credentials.py`

1. Setup Python Environment
2. Ensure Python 3.10 or newer is installed.
3. Install the necessary Python packages:

`pip install sqlalchemy kivy mysql-connector-python requests
`


To initialize the database schema and populate it with starter data:

`python installer.py`

To start the tracking application:

`python airport_main.py`


### Running
To run the travel planner app, import the project into your IDE of choice and 
create a new `.json` file titled `credentials.json` and by using the information
matching with the instructions in the example file, `credentials_example.json`. Then run `installer.py`
which will set up the tables in your database. After that point, run `travel_main.py` and use the Travel Planner App. 
