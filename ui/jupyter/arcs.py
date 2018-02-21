# -*- Python -*-
#
# Jiao Lin <jiao.lin@gmail.com>
#

from __future__ import print_function
from ipywidgets import interact, interactive
import ipywidgets as widgets
from IPython.display import display


def beam(): return Beam().createWidget()


class Beam:

    def __init__(self):
        self.params = dict()
        return
    
    def g(self, fc, fermi_nu, T0_nu, E, emission_time, ncount, nodes, with_moderator_angling):
        params = self.params
        try:
            T0_nu = float(T0_nu)
            E = float(E)
            emission_time = float(emission_time)
            ncount = int(float(ncount))
            print()
            params.update(
                fc=fc, fermi_nu=fermi_nu, T0_nu=T0_nu, E=E, emission_time=emission_time,
                ncount=ncount, nodes=nodes, with_moderator_angling=with_moderator_angling
            )
        except Exception as e:
            print("Wrong input.  %s" % e)
            self.params = dict()
        return

    def createWidget(self):
        w = interactive(
            self.g,
            fc=['100-1.5-SMI', '700-1.5-SMI', '700-0.5-AST'],
            fermi_nu=[600., 480., 360., 300.],
            T0_nu=["60.", "120."],
            E=widgets.Text("100."),
            emission_time=widgets.Text("-1."),
            ncount=widgets.Text("1e7"),
            nodes=(1,20),
            with_moderator_angling=True,
            )
        submit_button = widgets.Button(description="Submit")
        submit_button.on_click(self.simulate)
        panel = widgets.VBox(children=[w, submit_button])
        return panel

    def simulate(self, ev):
        params = self.params
        for k, v in params.items():
            print(k,v)
        return

    
# End of file 
