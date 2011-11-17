import mock

from responder import Responder

from responder.test import support
from responder.test.support import Expando

def pytest_funcarg__env(request):
    return support.fake_wsgi_env()

def pytest_funcarg__responder(request):
    return Responder(Expando())

def pytest_funcarg__default(request):
    default = mock.Mock()
    default.return_value = ('status', None, ('default response',))
    return default

def test_init_w_str():
    assert Responder('responder.labmod')

def test_init_w_obj():
    assert Responder(mock.Mock())

def test_root_to_default(env, default, responder):
    responder.handler.default = default
    start_resp = mock.Mock()
    env['PATH_INFO'] = '/'
    resp = responder(env, start_resp)
    start_resp.assert_called_with('status', [('Content-Type', 'text/html')])
    assert resp == ('default response',)

def test_root_to_root(env, default, responder):
    responder.handler.root = default
    start_resp = mock.Mock()
    env['PATH_INFO'] = '/'
    resp = responder(env, start_resp)
    start_resp.assert_called_with('status', [('Content-Type', 'text/html')])
    assert resp == ('default response',)
