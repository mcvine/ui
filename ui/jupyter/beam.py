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

def arcs():
    context = wiz.Context()
    step1 = Step1_Parameters(context)
    step1.show()
    return context


class ARCS:

    def __init__(self):
        self.params = dict()
        self.outdir = None
        return
    
    def setParams(self, fc, fermi_nu, T0_nu, E, emission_time, ncount, nodes, with_moderator_angling):
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

    def createForm(self):
        return interactive(
            self.setParams,
            fc=['100-1.5-SMI', '700-1.5-SMI', '700-0.5-AST'],
            fermi_nu=[600., 480., 360., 300.],
            T0_nu=["60.", "120."],
            E=ipyw.Text("100."),
            emission_time=ipyw.Text("-1."),
            ncount=ipyw.Text("1e7"),
            nodes=(1,20),
            with_moderator_angling=True,
            )


class Step1_Parameters(wiz.Step):

    def createPanel(self):
        self.text = text = ipyw.Text(description="Instrument beam configuration", place_holder='instrument')
        self.form_factory = ARCS()
        form = self.form_factory.createForm()
        OK = ipyw.Button(description='OK')
        OK.on_click(self.handle_next_button_click)
        widgets= [form, OK]
        return ipyw.VBox(children=widgets)

    def validate(self):
        params = self.form_factory.params
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
