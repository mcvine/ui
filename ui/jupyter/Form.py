# -*- Python -*-
#
# Jiao Lin <jiao.lin@gmail.com>
#

from __future__ import print_function
from ipywidgets import interact, interactive

class Parameter:

    name = None
    default = None
    range = None
    choices = None
    widget = None
    value = None
    converter = None

    def __init__(self, **kwds):
        assert 'name' in kwds, "must specify name"
        names = dir(self)
        for k,v in kwds.items():
            if k not in names:
                raise AttributeError(k)
            setattr(self, k, v)
        return
                

class FormFactory:

    P = Parameter
    parameters = None # overload this with parameters in the form

    def __init__(self):
        self.inputs = dict() 
        return
    
    def setParams(self, **kwds):
        inputs = self.inputs
        failed = False
        III = lambda x: x
        for p in self.parameters:
            try:
                inputs[p.name] = (p.converter or III)(kwds[p.name])
            except Exception as e:
                failed = e
                break
            continue
        if failed:
            print("Wrong input.  %s" % e)
            self.inputs = dict()
        else:
            print()
        return

    def createForm(self):
        kwds = dict()
        for p in self.parameters:
            v = p.widget or p.choices or p.range or p.default or p.value
            kwds[p.name] = v
            continue
        return interactive(self.setParams, **kwds)


# End of file 
