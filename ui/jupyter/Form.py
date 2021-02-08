# -*- Python -*-
#
# Jiao Lin <jiao.lin@gmail.com>
#

from __future__ import print_function
from ipywidgets import interact, interactive, interactive_output
import ipywidgets as ipyw
import collections

class Parameter:

    name = None
    label = None
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

    """
    ff = FormFactory()
    form = ff.createForm()
    frame = ipyw.VBox(children=[form])

    ff.inputs is a dictionary with all user inputs stored
    """

    def __init__(self):
        self.inputs = dict()
        # gather parameters and establish a map from name to parameter
        self.name2param = collections.OrderedDict()
        for p in self.__class__.parameters: self.name2param[p.name] = p
        self.parameters = list(self.name2param.values())
        # parameters are now unique.
        # For any duplicates, the later defines override the earlier ones
        return

    def createForm(self, preserve_order=False):
        kwds = dict()
        if preserve_order:
            widgets = []
            labels = []
        for p in self.parameters:
            if preserve_order:
                w = p.widget
                if w is None: raise RuntimeError("To preserve order, widget must be defined for each input")
                widgets.append(w)
                kwds[p.label or p.name] = w
                labels.append( ipyw.Label(value = p.label or p.name) )
            else:
                v = p.widget or p.choices or p.range or p.default or p.value
                kwds[p.label or p.name] = v
            continue
        if preserve_order:
            left = ipyw.VBox(labels)
            right = ipyw.VBox(widgets)
            form = ipyw.HBox([left, right])
            self.form_output = interactive_output(self.acceptInputs, kwds)
        else:
            form = interactive(self.acceptInputs, **kwds)
        form.add_class("wide-inputs") # allow customized css below
        return form

    def acceptInputs(self, **kwds):
        inputs = self.inputs
        failed = False
        III = lambda x: x
        for p in self.parameters:
            try:
                v = (p.converter or III)(kwds[p.label] if p.label in kwds else kwds[p.name])
                inputs[p.name] = v
            except Exception as e:
                failed = e
                break
            continue
        if not failed:
            try:
                self.crossCheckInputs()
            except Exception as e:
                failed = e
        if failed:
            print("Wrong input.  %s" % e)
            self.inputs = dict()
        else:
            print()
        return

    def crossCheckInputs(self):
        return


# XXX customize input label width XXX
from IPython.core.display import HTML
from IPython.display import display
display(HTML("""
<style>
.wide-inputs .widget-inline-hbox .widget-label {
  width: 140px;
}
</style>
"""))

# End of file 
