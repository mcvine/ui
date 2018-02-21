# -*- Python -*-
#
# Jiao Lin <jiao.lin@gmail.com>
#

from __future__ import print_function
from ipywidgets import interact, interactive
import collections

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
        # map name to parameter
        self.name2param = dict()
        for p in self.parameters: self.name2param[p.name] = p
        return
    
    def createForm(self):
        kwds = dict()
        for p in self.parameters:
            v = p.widget or p.choices or p.range or p.default or p.value
            kwds[p.name] = v
            continue
        return interactive(self.acceptInputs, **kwds)

    def acceptInputs(self, **kwds):
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


# End of file 
