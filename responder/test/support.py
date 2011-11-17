class Expando(object):
    """
    A completely promiscuous object.
    """
    def __init__(self, **attrs):
        self.update(attrs)

    def update(self, attrs):
        self.__dict__.update(attrs)
        return self

def fake_wsgi_env(**extra):
    env = {'QUERY_STRING': '',
           'PATH_INFO': '/example/path'}
