title: 2021 NFL Regular Season Schedule
published: 2021-06-06
tags: [nfl, football]

For the past few years, the NFL used to publish a graphics that showed the
entire regular season schedule for each team and each week at a glance, which
I always printed out and put on the kids’ door.

This year, unfortunately, I was not able to find a schedule for the upcoming
season, so I ended up creating one myself:

{{
   image(
       'nfl-schedule-2021.jpg', 
       'The 2021 NFL regular season schedule',
       'The 2021 NFL regular season schedule',
       class_name='here',
   )
}}

If you are interested in printable versions, you can download a [PDF
version](/static/files/nfl-schedule-2021.pdf) (7.3 MiB) or a [high-resolution
PNG image](/static/images/nfl-schedule-2021.full.png) (2100 × 1486, 1.8 MiB).

Creating the graphics was rather straightforward: I wrote a small Python
script where I added the schedule information in a suitable data structure,
and then used [Jinja](https://jinja.palletsprojects.com/) to render a simple
HTML table with the desired layout.  After downloading the team and NFL logos
as SVGs, all that was left to be done was to sprinkle in some [elementary
CSS](https://gehtsscheissn.at), and print the resulting page into a PDF
file—that’s it!
