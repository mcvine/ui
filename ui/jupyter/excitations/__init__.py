# -*- Python -*-
#
# Jiao Lin <jiao.lin@gmail.com>
#

import os
def validate_path(p):
    if not p:
        raise ValueError("Empty")
    p = os.path.abspath(p)
    assert os.path.exists(p)
    assert p.endswith('.h5')
    # if isinstance(p, unicode): p = p.encode()
    return p

def validate_range(unit):
    def _to_q(v):
        return '%s*%s' % (v, unit)
    def _(qr):
        qr = eval(qr)
        qr = list(map(float, qr))
        qr = list(map(_to_q, qr))
        s =  ','.join(qr)
        # if isinstance(s, str): s = s.encode()
        return s
    return _

from ..excitation import Excitation as ExcitationBase, FormFactory, Step4a_ExcitationConfig

# End of file 
