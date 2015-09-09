__author__ = 'dracks'


import httplib
import json

class Response:
    def __init__(self, request_headers, response_headers, response_status, response_body):
        self.request_headers=request_headers
        self.response_header=response_headers
        self.response_status=response_status
        self.response_body=response_body


class Connector:

    def __init__(self, server, path, token):
        self.token=token
        self.server=server
        self.path=path
        self.port = 80

    def request_data(self, method, endpoint, data):
        """

        :param method:
        :param endpoint:
        :param data:
        :return:
        :rtype: Response
        """
        connection=httplib.HTTPConnection(self.server, self.port)
        # connection.set_debuglevel(1)
        header={
            'Token':self.token,
            'Host': self.server,
            'User-agent': 'apiTester/0.8',
            #'content-type' :'application/javascript',
        }
        call=self.path+endpoint

        connection.request(method, call, data, header)
        response=connection.getresponse()
        responseHeaders={}
        for par in response.getheaders():
            responseHeaders[par[0]]=par[1]

        return Response(header, responseHeaders, response.status, response.read())