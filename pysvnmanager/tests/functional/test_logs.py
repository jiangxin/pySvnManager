from pysvnmanager.tests import *

class TestLogsController(TestController):

    def test_index(self):
        response = self.app.get(url_for(controller='logs'))
        # Test response...
