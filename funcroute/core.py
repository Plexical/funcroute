import os
from collections import deque

from wsgiref.simple_server import make_server
from cgi import parse_qs, escape

class Missing(Exception):
    pass

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

        path, args = self.parse_input(env)
        named = getattr(self.handler, path and path[0] or 'root', False)
        try:
            if named:
                status, headers, response = named(*path, **args)
            elif self.app:
                return self.app(env, start_response)
            else:
                try:
                    status, headers, response = self.handler.default(*path,
                                                                      **args)
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

if __name__ == '__main__':
    rsp = Matcher('labmod')
    httpd = make_server('', 8000, rsp)
    httpd.serve_forever()
