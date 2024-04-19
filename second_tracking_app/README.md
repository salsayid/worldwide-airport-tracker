**Airport Tracker System**

**Application Names**

* Tracking App: Airport Tracker

* Database Installer: Airport Installer



****Completeness and Correctness****

**Airport Tracker**
* Status: The application is functional but still in the development phase.

* Known Issues: API key for weather data fetching is hardcoded, which might not be secure. Some error handling for database operations is not fully implemented.

**Airport Installer**
* Status: The installer can create and populate the database but lacks robust error handling.
* Known Issues:Does not handle database connection failures gracefully.



**Building and Running the Applications**

Both applications require:

* Python 3.10
* SQLAlchemy
* Kivy (for GUI)
* mysql-connector-python
* requests (for API calls)


1. Setup Python Environment
2. Ensure Python 3.8 or newer is installed.
3. Install the necessary Python packages:

`pip install sqlalchemy kivy mysql-connector-python requests
`

Database Setup
Set up a MySQL database with the following credentials:
* Username: salsayid2
* Password: cho1ooWaew9u
* Database Name: salsayid2
* Host: localhost
* Port: 3306

To initialize the database schema and populate it with starter data:

`python airport_installer.py`

To start the tracking application:

`python main.py`