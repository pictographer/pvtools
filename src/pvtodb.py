import sys
from lxml import etree

from pvextract.pvextract import PVExtract

path = '../test/data/2017-05-02T06:15-0700/192.168.1.215/'
home_file = path + 'home.html'
production_file = path + 'production.html'
production_label ="Currently generating"
version_label = "Current Software Version"
checked_version = "R3.7.28 (88072d)"

home_extract = PVExtract(home_file)
observed_version = home_extract.next_text(version_label)
if observed_version != checked_version:
    print("{}:Warning: version has changed from {} to {}." .
          format(sys.argv[0], checked_version, observed_version))
home_production = home_extract.next_text(production_label)
print("{}: {}".format(production_label, home_production))

production_extract = PVExtract(production_file)
for field_label in ["Currently", "Today", "Past Week"]:
    field_value = production_extract.next_text(field_label)
    print("{}: {}".format(field_label, field_value))
