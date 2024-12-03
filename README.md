# HapPy Pots
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
![](HaPy Pots app.gif)
*Screen recorded with Gifcap by [joaomoreno](https://github.com/joaomoreno/gifcap)*
