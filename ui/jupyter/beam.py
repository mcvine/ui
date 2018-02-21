# -*- Python -*-
#
# Jiao Lin <jiao.lin@gmail.com>
#

from __future__ import print_function
import os
from ipywidgets import interact, interactive
import ipywidgets as ipyw
from IPython.display import display
import ipywe.fileselector
import ipywe.wizard as wiz
from .Form import FormFactory

def arcs():
    context = wiz.Context()
    step1 = Step1_Parameters(context)
    step1.show()
    return context


class DGS(FormFactory):

    P = FormFactory.P
    parameters = [
        P(name="nominal_energy", widget=ipyw.Text("100."), converter=float),
        P(name="emission_time", widget=ipyw.Text("01."), converter=float),
        P(name="neutron_count", widget=ipyw.Text("1e7"), converter=lambda x: int(float(x))),
        P(name="nodes", range=(1,20)),
    ]


class ARCS(DGS):

    P = FormFactory.P
    parameters = DGS.parameters + [
        P(name="fermi_chopper", choices=['100-1.5-SMI', '700-1.5-SMI', '700-0.5-AST']),
        P(name="fermi_frequency", choices=[600., 480., 360., 300.]),
        P(name="T0_frequency", choices=["60.", "120."], converter=float),
        P(name="with_moderator_angling", default=True),
    ]
    
        
class SEQUOIA(DGS):

    P = FormFactory.P
    parameters = DGS.parameters + [
        P(name="fermi_chopper", choices=['100-2.03-AST', '700-3.56-AST','700-0.5-AST']),
        P(name="fermi_frequency", choices=[600., 480., 360., 300.]),
        P(name="T0_frequency", choices=["60.", "120."], converter=float),
    ]
    
        
class Step1_Parameters(wiz.Step):

    def createPanel(self):
        self.title = title = ipyw.Label("Beam configuration")
        self.form_factory = ARCS()
        form = self.form_factory.createForm()
        OK = ipyw.Button(description='OK')
        OK.on_click(self.handle_next_button_click)
        widgets= [title, form, OK]
        return ipyw.VBox(children=widgets)

    def validate(self):
        params = self.form_factory.inputs
        # check user input
        if not params:
            print("Please check your inputs")
            return False
        self.context.params = params # save user input
        return True
    
    def nextStep(self):
        step2 = Step2_Outdir(self.context)
        step2.show()
        
class Step2_Outdir(wiz.Step):
    
    def createPanel(self):
        self.select = ipywe.fileselector.FileSelectorPanel(
            instruction='select output directory', start_dir=os.path.expanduser('~'), type='directory',
            next=self.on_sel_outdir
        )
        widgets= [self.select.panel]
        return ipyw.VBox(children=widgets)

    def on_sel_outdir(self, selected):
        self.context.outdir = selected
        return self.nextStep()
    
    def nextStep(self):
        return self.simulate()
    
    def simulate(self):
        print(self.context)
        params = self.context.params
        for k, v in params.items():
            print(k,v)
        print(self.context.outdir)
        return


# End of file 
