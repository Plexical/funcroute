import webtest
import mock

from json import loads, dumps

from funcroute import *

from funcroute.test import support
from funcroute.test.support import Expando

def pytest_funcarg__responder(request):
    return Matcher(Expando())

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
    assert Matcher('funcroute.labmod')

def test_init_w_obj():
    assert Matcher(mock.Mock())

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

def test_text_defaults():
    assert text('foo') == ('200 OK', {'Content-Type': 'text/plain'}, ('foo',))

def test_text_defaults():
    assert html('foo') == ('200 OK', {'Content-Type': 'text/html'}, ('foo',))

def test_html_other_status():
    assert (html('foo', '404 NOT FOUND') ==
            ('404 NOT FOUND', {'Content-Type': 'text/html'}, ('foo',)) )

def test_post(wtfix):
    handler, responder, wt = wtfix

    handler.api = (lambda req, *segs:
                       json(loads(req.body)) )

    res = wt.post('/api',
                  dumps('foo'),
                  {'Content-Type': 'application/json'})

    assert (res ==
            '200 OK', {'Content-Type': 'application/json'}, '"foo"')
