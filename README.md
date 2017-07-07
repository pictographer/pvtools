# pvtools
_Tools for scraping and analyzing data from my photovoltaic power system_

**Keywords: Python 3, lxml, psycopg2, PostgreSQL, ETL**

## Introduction

The controller for my photovoltaic system hosts a webserver that provides
system status including the current production of the system. It does not
provide long-term logging or data analysis.

Several years ago, I created a cron job to sample the state of the system
every five minutes. The script to do this is simple. It uses wget to download
the files.

```cd /home/pv/envoy
wget \
    --append-output=solar.log \
    --no-cookies \
    --directory-prefix=$(date -Iminute) \
    --adjust-extension \
    --convert-links \
    --page-requisites \
    --execute robots=off \
    --no-parent \
    http://192.168.1.215/home \
    http://192.168.1.215/production
```

At the time, I needed get something running quickly. Solar City sent
us a notice that we would lose our nice 3rd party monitoring by
Enphase Energy if we didn't pay them a bunch of money to install their
new system. The notice eventually turned out to be false.

The `wget` approach is successful in that it does capture all the data
and will continue to do so even if the output format changes (provided
the URLs remain unchanged). However, the data is uncompressed,
contains redundant files, and requires additional steps to extract the
useful information.

The goals of this project are to extract the data into a more useful and more
compact form while demonstrating what's possible in a few lines of Python. I've
tried to strike a compromise between a quick-but-brittle hack and a general
system that might handle many more use cases than I have.

At a minimum, monitoring and logging should report the following:

* System outages
* Production on the peak day of the year
* Total production for the year

We monitor system outages via an indicator LED. Now that we know the
remote monitoring isn't going away, relying on an email from Enphase
if we don't happen to notice the LED is fine for now.

Due to weather and pollution, PV output varies from year to year, but
peak production and annual production tell us how the system is
degrading over time.

Here's a brittle hack I've used grep to pluck out the current production:

```
wget -qO- http://192.168.1.215/home|grep -o "generating.*"|grep -o "[0-9.][0-9.]*"
```

This pipes `home.html` to grep matching all lines containing the word
'generating' and outputing line from the word 'generating' on. The second grep
extracts the longest sequence of one or more digits. What could go wrong? Well,
the units of the number change depending its magnitude, for one thing. It works
for setting an indicator light when the panels are generating non-zero power.
But more importantly, this expression doesn't offer much in the way of error
detection and this style is too cryptic for a team effort. Which brings us to
Python.

## System Overview

The main code is `pvtodb.py`.

```Usage:
    python3 pvtodb.py dir1 [dir2 ...]
```
`pvtodb` does three things:

* Looks for specific HTML file names
* Parses the HTML
* Extracts selected table values
* Writes the values to a PostgreSQL database

## External Libraries

The libraries available make short work of this and give much improved
functionality.

[lxml](http://lxml.de/) provides a Python interface to
[libxml2](http://xmlsoft.org/) and [xslt](http://xmlsoft.org/XSLT/). **lxml**
parses the HTML for us and allows us to use high-level patterns on the structure
of the HTML to extract the data.

[psycopg2](https://wiki.postgresql.org/wiki/Psycopg2) provides a Python
interface to [PostgreSQL](https://www.postgresql.org/). (In case you're
wondering why I didn't use a spreadsheet, I've got over 150k data points to
analyze and it was time to refresh my database skills.)

[dateutil](https://dateutil.readthedocs.io/en/stable/) provides a way to detect
badly formatted dates. This is most likely to happen if `pytodb` is given an
invalid directory, but that's easy to do.

I explored using one of the many libraries that offers unit checking for
numerical values such as [pint](https://pint.readthedocs.io/en/0.7.2/), but
decided it would be more work to find the best one than to write a seven-line
function.

## Handy SQL Queries

Show the production for each week:

```sql
SELECT *
FROM
  (SELECT extract(week FROM TIME) AS w,
          extract(YEAR FROM TIME) AS y,
	  max(week_wh) AS max_wh
   FROM production GROUP BY w, y) a
ORDER BY 100 * y + w;
```

