
Alarms and dashboards
=====================

:slug: alarms_and_dashboards
:categories: Articles
:tags: rants, alarm, dashboard, DevOps, errors
:date: 2021-06-04 12:00
:summary: Ranting about alarms and dashboards


Dashboard is a great tool to show information in a human-friendly manner.
Yet, it is useless as a monitoring tool.
Hanging a big shiny screen in the middle of the room, with bars, plots,
charts and lots of other cool stuff is spectacular.
But it won't help you to catch an issue in a timely manner.
That is because you can't watch the screen all the time, don't you?

The solution is obvious - alarms.
Alarms are meant to warn you when the situation is exceptional or
something is about to go south. When a service fails.
When your disk space is running low.
When a request processing time takes too long.
When there is an error in logs.

And then, you actually need a dashboard to query the history
of the parameters in trouble.
You'd want to see the trend of free disk space - did it happen suddenly,
or it's been filling up in a linear manner?
Maybe you have to wipe some old data?
Perhaps there was a temporal network error?
How many times that error happened lately?

Alarm can be dangerous.
When you get too many alarms they slip through.
Too many "usual" alarms turn into annoying buzz which is soon ignored.
The solution is to temporarily disable the unnecessary alarms.
Do keep in mind that
**an alarm could be disabled only when you are actively fixing the problem**.

This is nothing new.
Have you seen Ron Howard's "Apollo 13" film?
Remember the CO2 alarm indicator lighting up and the crew checking
the CO2 levels on the gauge?


.. image:: {static}/images/articles/2021_06_04_alarms_and_dashboards/apollo_13_co2_indicator.jpg
   :align: center
   :width: 50%
   :alt: CO2 Indicator | Apollo 13 (2005)

Can you imagine the crew constantly checking those values
to make sure that CO2 levels are acceptable instead?
What about other critical indicators?
Of course not.

.. image:: {static}/images/articles/2021_06_04_alarms_and_dashboards/apollo_13_co2_gauge.jpg
   :align: center
   :width: 50%
   :alt: CO2 Gauge | Apollo 13 (2005)

There are alarms to draw attention and dashboards to help dealing with the alarm as fast as possible.
