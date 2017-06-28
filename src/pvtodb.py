import sys
import re
from lxml import etree

data_file = '../test/data/2017-05-02T06:15-0700/192.168.1.215/home.html'
production_label = 'Currently generating'
version_label = 'Current Software Version'
checked_version = 'R3.7.28 (88072d)'

# The PV output is reported in a table. The header uses td markup and
# has the text defined above as label. The value we seek is the text
# of the next td element. This function returns the text of the next
# td element following a td with the given label text.
def successor_text(root, label):
    xpath_pat = './/td[text()="{}"]/following-sibling::td'.format(label)
    head = root.xpath(xpath_pat)
    assert(len(head) == 1)
    return head[0].text.strip()

# The input files are short. Read the entire thing.
raw_html = open(data_file, 'r').read()
try:
    root = etree.HTML(raw_html)
except Exception as e:
    print(repr(e))

observed_version = successor_text(root, version_label)
if observed_version != checked_version:
    print("{}:Warning: version has changed from {} to {}." .
          format(sys.argv[0], checked_version, observed_version))

# Report the power generated.
print(successor_text(root, production_label))
