import os
from collections import deque

import webob

from wsgiref.simple_server import make_server
from cgi import parse_qs, escape

name = 'funcroute'
version = '0.2dev'

class Missing(Exception):
    pass

def segment(request):
    return deque(s for s in request.path.split('/') if s)

class Matcher(object):

    def __init__(self, handler, app=None):
        if isinstance(handler, basestring):
            self.handler = __import__(handler)
        else:
            self.handler = handler
        self.debug = getattr(self.handler, 'debug', False)
        self.lastmod = self.mtime
        self.app = app

    @property
    def mtime(self):
        if hasattr(self.handler, '__file__'):
            return os.stat(self.handler.__file__).st_mtime
        return 0

    def parse_input(self, env):
        path = deque(s for s in env['PATH_INFO'].split('/') if s)
        qs = env.get('QUERY_STRING', False)
        return path and path or tuple(), qs and parse_qs(qs) or {}

    def maybee_reload(self):
        mtime = self.mtime
        if mtime > self.lastmod:
            print('Matcher: changes to module detected, reloading..')
            self.handler = reload(self.handler)
            self.debug = getattr(self.handler, 'debug', False)
            self.lastmod = mtime

    def __call__(self, env, start_response):
        if self.debug:
            self.maybee_reload()

        request = webob.Request(env)
        segs = segment(request)

        named = getattr(self.handler, segs and segs[0] or 'root', False)
        try:
            if named:
                status, headers, response = named(request, *segs)
            elif self.app:
                return self.app(env, start_response)
            else:
                try:
                    status, headers, response = self.handler.default(request,
                                                                     *segs)
                except AttributeError:
                    raise Missing

            if not headers:
                headers = {'Content-Type': 'text/html'}
            start_response(status, [(k, v) for k, v in headers.iteritems()])
            return ('\n'.join(response),)
        except StandardError, e:
            start_response('500 INTERNAL SERVER ERROR',
                           [('Content-Type', 'text/plain')])
            return ('Internal server error',)
        except Missing, e:
            start_response('404 NOT FOUND',
                           [('Content-Type', 'text/plain')])
            return ('Resource not found',)

def send(body, mime='text/html', status='200 OK', **extra_headers):
    headers = {'Content-Type': mime}
    headers.update(extra_headers)
    return (status, headers, (body,))

def text(body, status='200 OK', **extra_headers):
    return send(body, 'text/plain', status, **extra_headers)

def html(body, status='200 OK', **extra_headers):
    return send(body, 'text/html', status, **extra_headers)

def json(data, status='200 OK', **extra_headers):
    from json import dumps
    return send(dumps(data),
                'application/json',
                status=status,
                **extra_headers)

if __name__ == '__main__':
    rsp = Matcher('labmod')
    httpd = make_server('', 8000, rsp)
    httpd.serve_forever()
