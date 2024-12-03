# HaPy Pots
A collaboration project with my girlfriend for a Python developer program in 2020.

## Short description
Web app that features plant pots equiped with sensors that care about plant wellbeing.
It enables users to create their account and insert information about their plants, plant
requirements, and location of the plant pot. In return, sensors monitor changes in the air
and the soil (RaspberryPi simulations) and take action to make sure plants are happy in
their environment.

## App features
- homepage intro
- login/logout -> should've added option "forgot your password?"
- CRUD databases, UI
- fetches min and max city temperature from daily DHMZ xml file; returns average
- in combination with RaspberryPi simulates plant conditions (sunlight,humidity, saltiness, fertilizer)
- provides a plot of values for each pot

### Preview
![](HaPy_Pots_preview.gif)
*Screen recorded with Gifcap by [joaomoreno](https://github.com/joaomoreno/gifcap)*

## Usage
As the project isn't connected to the WSGI server yet, the only way of checking the features is to
download the development version.
All required libraries to run the project can be found in the `requirement.txt` file. It is recommended
to set up a [virtual environment](https://docs.python.org/3/library/venv.html), and install all libraries 
there to avoid unexpected issues of running the Flask app (for this project, the virtual environment folder was
named `hapy_pots_venv`).
**diclaimer:**
*To run the project completely, both `HaPy Pots` and `HRPi` folders are required, as the second one runs on the RaspberryPi
virtual machine to mimic sensor changes. The app runs fine without it, but "Refresh" buttons will not work, as the RPi
database won't be available.*

### Steps
1. download the `HaPy Pots` file to your computer
2. set up a virtual environment for the project and activate it
3. `pip install -r requirements.txt`
4. `flask run`
5. open the link generated in terminal
