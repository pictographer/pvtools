from pvextract import PVExtract

path = '../../test/data/2017-05-02T06:15-0700/192.168.1.215/'
home_file = path + 'home.html'
extractor = PVExtract(home_file)

def test_next_text():
    assert("3.79 W" == extractor.next_text("Currently generating"))

def test_version():
    assert("R3.7.28 (88072d)"
           == extractor.next_text("Current Software Version"))

if __name__ == '__main__':
    test_version()
    test_next_text()
