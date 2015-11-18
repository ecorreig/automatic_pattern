import EndpointProperties
from EndpointModel import Model as AbstractModel

class ApiSession(AbstractModel):
    _name = ['apiSession', 'apiSessions']
    _fields = ['id', 'token', 'renew', 'expiration']
    expiration = EndpointProperties.DateProperty()
