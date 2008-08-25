from pysvnmanager.tests import *

class TestReposController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='repos'))
        # Test response...
