from responder import Responder

from responder.test.support import Expando

def test_init_w_str():
    assert Responder('labmod')

def test_init_w_obj():
    assert Responder(Expando())
