from lxml import etree


class PVExtract:
    '''Provides structured access to the contents of an HTML file.'''

    def __init__(self, html_path):
        '''Read and parse the HTML data_file, returning the lxml parse tree.'''

        # The input files are short. Read and parse the entire thing.
        with open(html_path, 'r') as raw_html:
            self.root = etree.HTML(raw_html.read())

    def next_text(self, label, tag='td'):
        xpath_pat = \
            './/{}[text()="{}"]/following-sibling::{}'.format(tag, label, tag)
        head = self.root.xpath(xpath_pat)
        assert(len(head) == 1)
        return head[0].text.strip()

if __name__ == '__main__':
    path = '../../test/data/2017-05-02T06:15-0700/192.168.1.215/'
    home_file = path + 'home.html'
    production_label = "Currently generating"
    result = PVExtract(home_file).next_text(production_label)
    print("{}: {}".format(production_label, result))
