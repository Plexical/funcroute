debug = True

def default(*path, **args):
    return '200 OK', None, (l for l in ('Hello', 'World'))

def api(*path, **args):
    return '200 OK', None, ['api']
