import os
from collections import deque

from wsgiref.simple_server import make_server
from cgi import parse_qs, escape

class Handler(object):

    def __init__(self, name):
        self.name = name
        m = self.mod = __import__(name)
        self.debug = getattr(m, 'debug', False)
        self.lastmod = self.mtime

    @property
    def mtime(self):
        return os.stat(self.mod.__file__).st_mtime

    def parse_input(self, env):
        path = deque(s for s in env['PATH_INFO'].split('/') if s)
        qs = env.get('QUERY_STRING', False)
        return path, qs and parse_qs(qs) or {}

    def __call__(self, env, start_response):
        if self.debug:
            mtime = self.mtime
            if mtime > self.lastmod:
                print('Changes to module detected, reloading..')
                self.mod = reload(self.mod)
                self.debug = getattr(self.mod, 'debug', False)
                self.lastmod = mtime

        path, args = self.parse_input(env)

        if len(path) == 0:
            status, headers, response = self.mod.default(*path)
        else:
            status, headers, response = getattr(self.mod, path[0])(*path)

        try:
            if not headers:
                headers = {'Content-Type': 'text/html'}
            start_response(status, [(k, v) for k, v in headers.iteritems()])
            return ('\n'.join(response),)
        except AttributeError, e:
            start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
            return ('XXX TBD: Response method not found',)
        except StandardError, e:
            start_response('500 INTERNAL SERVER ERROR',
                           [('Content-Type', 'text/plain')])
            return ('XXX TBD: Response method raised exception',)

if __name__ == '__main__':
    rsp = Handler('labmod')
    httpd = make_server('', 8000, rsp)
    httpd.serve_forever()
