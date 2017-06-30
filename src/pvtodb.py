# Extract, transform, and load photovoltaic production values from a collection
# of web pages. The data gets written to a PostgreSQL database.

import sys
import os
from os.path import split as pf
import dateutil.parser

from lxml import etree
import psycopg2

from pvextract.pvextract import PVExtract

usage = "Usage:\n    python3 pvtodb.py dir1 [dir2 ...]"

# Constants for home.html
production_label ="Currently generating"
version_label = "Current Software Version"
checked_version = "R3.7.28 (88072d)"

# Constants for production.html and the pvdb.production database table
# Note: The entries in html_fields correspond to the second and subsequent
# database columns in db_columns.
html_fields = ["Currently", "Today", "Past Week"]
db_credentials = 'dbname=pvdb user=corbett password=xxxxxxx'
db_columns = ('time timestamp with time zone primary key,'
              'power_W real,'
              'day_Wh real,'
              'week_Wh real')

def path_timestamp(path):
    '''Extract the timestamp from the given path.
    
    Assumes the time stamp is the third to last path component.
    E.g. .../third/second/last ==> third'''

    # Recall pf is os.path.split() and this function returns a pair
    # (path, basename).
    result = pf(pf(pf(path)[0])[0])[1]
    # The dateutil package conveniently parses ISO 8601 dates with time zones.
    assert(dateutil.parser.parse(result))
    return result

def doraise(err):
    raise err

def normalize_units(quantity):
    '''Convert a string "<float> <unit>" to a float scaled to the base unit.
    
    For any unit that contains a scaling factor, scale the float so that
    no conversion factor is needed. For example 2 kW returns 2000.0. If the
    unit designator is not recognized, KeyError is raised.'''

    (x, units) = quantity.split()
    unit_factors = {"W": 1.,
                    "kW": 1e3,
                    "Wh": 1.,
                    "kWh": 1e3}
    return float(x) * unit_factors[units]

def pv_insert(con, cur, root):
    '''Extract html data from root. Insert it using cursor cur.'''

    # For each directory containing home.html and production.html,
    # extract the data and insert it into the db.
    #
    # If anything other than a version check fails, raise an error.
    for (path, _, filenames) in os.walk(root, onerror=doraise):
        if set(filenames) >= set(['home.html', 'production.html']):
            home_file = os.path.join(path, 'home.html')
            production_file = os.path.join(path, 'production.html')

            home_extract = PVExtract(home_file)
            observed_version = home_extract.next_text(version_label)
            if observed_version != checked_version:
                print("{}:Warning: version has changed from {} to {}."
                      .format(sys.argv[0],
                              checked_version,
                              observed_version))

            production_extract = PVExtract(production_file)
            values = (
                [path_timestamp(home_file)]
                + [str(normalize_units(production_extract.next_text(f)))
                   for f in html_fields])

            cur.execute('insert into production '
                        'values (%s, %s, %s, %s)',
                        (values[0], values[1], values[2], values[3]))
    con.commit()

def pv_etl(dirlist):
    '''Connect to the database and load data from dirlist.'''
    with psycopg2.connect(db_credentials) as con:
        with con.cursor() as cur:
            cur.execute('create table if not exists production ({})'
                        .format(db_columns))
            for root in dirlist:
                pv_insert(con, cur, root)

if __name__ == '__main__':
    if 1 < len(sys.argv):
        pv_etl(sys.argv[1:])
    else:
        print(usage)
