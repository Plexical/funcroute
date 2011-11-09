import os
from collections import deque

from wsgiref.simple_server import make_server
from cgi import parse_qs, escape

class Responder(object):

    def __init__(self, module, app=None):
        if isinstance(module, 'basestring'):
            self.mod = __import__(module)
        else:
            self.mod = module
        self.debug = getattr(self.mod, 'debug', False)
        self.lastmod = self.mtime
        self.app = app

    @property
    def mtime(self):
        return os.stat(self.mod.__file__).st_mtime

    def parse_input(self, env):
        path = deque(s for s in env['PATH_INFO'].split('/') if s)
        qs = env.get('QUERY_STRING', False)
        return path, qs and parse_qs(qs) or {}

    def maybee_reload(self):
        mtime = self.mtime
        if mtime > self.lastmod:
            print('Responder: changes to module detected, reloading..')
            self.mod = reload(self.mod)
            self.debug = getattr(self.mod, 'debug', False)
            self.lastmod = mtime

    def __call__(self, env, start_response):
        if self.debug:
            self.maybee_reload()

        path, args = self.parse_input(env)
        named = getattr(self.mod, path[0], False)
        if named:
            status, headers, response = named(*path, **args)
        elif self.app:
            return self.app(env, start_response)
        else:
            status, headers, response = self.mod.default(*path, **args)

        try:
            if not headers:
                headers = {'Content-Type': 'text/html'}
            start_response(status, [(k, v) for k, v in headers.iteritems()])
            return ('\n'.join(response),)
        except StandardError, e:
            start_response('500 INTERNAL SERVER ERROR',
                           [('Content-Type', 'text/plain')])
            return ('XXX TBD: Response method raised exception',)

if __name__ == '__main__':
    rsp = Responder('labmod')
    httpd = make_server('', 8000, rsp)
    httpd.serve_forever()