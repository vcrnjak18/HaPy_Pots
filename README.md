# HapPy Pots

Web app that features plant pots equiped with sensors that care about plant wellbeing.
It enables users to create their account and insert information about their plants, plant
requirements, and location of the plant pot. In return, sensors monitor changes in the air
and the soil (RaspberryPi simulations) and take action to make sure plants are happy in
their environment.


Web app features:
- homepage intro
- login/logout -> should've added option "forgot your password?"
- add, edit, delete users (themselves)
- add, edit, delete plants and pots
- fetches min and max city temperature from daily DHMZ xml file; returns average
- in combination with RaspberryPi simulations returns plant conditions (sunlight,humidity, saltiness, fertilizer)
- provides a plot of values for each pot
