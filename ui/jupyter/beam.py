# -*- Python -*-
#
# Jiao Lin <jiao.lin@gmail.com>
#

from __future__ import print_function
import os
from ipywidgets import interact, interactive
import ipywidgets as widgets
from IPython.display import display
import ipywe.fileselector

def arcs(): return ARCS().createWidget()


class ARCS:

    def __init__(self):
        self.params = dict()
        self.outdir = None
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
        self.form = w = interactive(
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
        #
        outdir_sel= ipywe.fileselector.FileSelectorPanel(
            instruction='select output directory', start_dir=os.path.expanduser('~'), type='directory',
            next=self.on_sel_outdir
        )
        #
        self.submit_button = submit_button = widgets.Button(description="Submit")
        submit_button.on_click(self.simulate)
        self.panel = panel = widgets.VBox(children=[w, outdir_sel.panel, submit_button])
        return panel

    def on_sel_outdir(self, selected):
        self.outdir = selected
        self.panel.children = [self.form, widgets.Label("Selected output dir: %s" % selected), self.submit_button]
        return

    def simulate(self, ev):
        params = self.params
        for k, v in params.items():
            print(k,v)
        print(self.outdir)
        return

    
# End of file 
