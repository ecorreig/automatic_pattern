__author__ = 'dracks'

from Api.Manager import DataManager
from Api.Connector import Response

class MockConnector:
    def request_data(self, endpoint, data):
        return Response(None, None, None, data)
DataManager._get_connection = lambda config: MockConnector()
DataManager.__manager = DataManager()

from Api.EndpointProperties import DateProperty
import dateutil.parser

from tests import *
from Api.tests import *



if __name__ == '__main__':
    unittest.main()
