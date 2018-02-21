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

def beam():
    context = wiz.Context()
    step1 = Step0_Instrument(context)
    step1.show()
    return context


class DGS(FormFactory):

    P = FormFactory.P
    # names must match parameters in "mcvine <instrument> beam" CLI
    parameters = [
        P(name='E', label="Nominal energy", widget=ipyw.Text("100."), converter=float),
        P(name='emission_time', label="Emission time", widget=ipyw.Text("-1."), converter=float),
        P(name='ncount', label="Neutron count", widget=ipyw.Text("1e7"), converter=lambda x: int(float(x))),
        P(name="nodes", label="Number of cores", range=(1,20)),
    ]


class ARCS(DGS):

    P = FormFactory.P
    parameters = DGS.parameters + [
        P(name="fermi_chopper", label="Fermi chopper", choices=['100-1.5-SMI', '700-1.5-SMI', '700-0.5-AST']),
        P(name="fermi_nu", label="Fermi chopper frequency", choices=[600., 480., 360., 300.]),
        P(name="T0_nu", label="T0 chopper frequency", choices=["60.", "120."], converter=float),
        P(name="with_moderator_angling", default=True),
    ]
    
        
class SEQUOIA(DGS):

    P = FormFactory.P
    parameters = DGS.parameters + [
        P(name="fermi_chopper", label="Fermi chopper", choices=['100-2.03-AST', '700-3.56-AST','700-0.5-AST']),
        P(name="fermi_nu", label="Fermi chopper frequency", choices=[600., 480., 360., 300.]),
        P(name="T0_nu", label="T0 chopper frequency", choices=["60.", "120."], converter=float),
    ]
    
        
class Step0_Instrument(wiz.Step):

    def createPanel(self):
        self.title = title = ipyw.HTML("<h4>Choose instrument</h4>")
        self.select = ipyw.Dropdown(options=['ARCS', 'SEQUOIA'], value='ARCS', description='Insturment:')
        OK = ipyw.Button(description='OK')
        OK.on_click(self.handle_next_button_click)
        widgets= [self.title, self.select, OK]
        return ipyw.VBox(children=widgets)

    def validate(self):
        self.context.instrument = self.select.value
        return True
    
    def nextStep(self):
        step1 = Step1_Parameters(self.context)
        step1.show()
        
class Step1_Parameters(wiz.Step):

    def createPanel(self):
        self.title = title = ipyw.HTML("<h4>Beam configuration</h4>")
        self.form_factory = eval(self.context.instrument)()
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
            instruction='Select output directory', start_dir=os.path.expanduser('~'), type='directory',
            next=self.on_sel_outdir, newdir_toolbar_button=True
        )
        widgets= [self.select.panel]
        return ipyw.VBox(children=widgets)

    def on_sel_outdir(self, selected):
        self.context.outdir = selected
        return self.nextStep()
    
    def nextStep(self):
        return self.simulate()
    
    def simulate(self, dry_run=True):
        if dry_run:
            params = self.context.params
            cmd = 'cd ' + self.context.outdir + '; mcvine instruments ' + self.context.instrument.lower()
            for k, v in params.items(): cmd += ' --%s=%r' % (k,v)
            print(cmd)
            return
        return


# End of file 
