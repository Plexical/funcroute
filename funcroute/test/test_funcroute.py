import webtest
import mock

from funcroute import Responder

from funcroute.test import support
from funcroute.test.support import Expando

def pytest_funcarg__responder(request):
    return Responder(Expando())

def pytest_funcarg__default(request):
    default = mock.Mock()
    default.return_value = ('200 OK', None, ('default response',))
    return default

def pytest_funcarg__wtfix(request):
    responder = pytest_funcarg__responder(request)
    return (responder.handler, responder, webtest.TestApp(responder))

def pytest_funcarg__defaultfix(request):
    (handler, responder, wt), default = (pytest_funcarg__wtfix(request),
                                         pytest_funcarg__default(request))
    handler.default = default
    return (handler, responder, wt, default)

def test_init_w_str():
    assert Responder('funcroute.labmod')

def test_init_w_obj():
    assert Responder(mock.Mock())

def test_root_to_default(defaultfix):
    handler, responder, wt, default = defaultfix
    res = wt.get('/')
    assert res.status_int == 200
    assert res.normal_body == 'default response'

def test_root_to_root(wtfix, default):
    handler, responder, wt = wtfix
    handler.root = default
    res = wt.get('/')
    assert res.status_int == 200
    assert res.normal_body == 'default response'

def test_any_to_default(defaultfix):
    handler, responder, wt, default = defaultfix
    res = wt.get('/whatever')
    assert res.status_int == 200
    assert res.normal_body == 'default response'

def test_missing(wtfix):
    handler, responder, wt = wtfix
    res = wt.get('/unavailable', status=404)
