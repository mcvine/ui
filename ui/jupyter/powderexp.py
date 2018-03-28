# -*- Python -*-
#
# Jiao Lin <jiao.lin@gmail.com>
#


"""
* Choose beam
* Choose sample
  - choose directory or template
  - if template
    - choose name
    - choose temperature
    - choose shape
* Choose simulation parameters
  - ncount
  - nodes
* Generate the simulate folder, and give instructions

"""

from __future__ import print_function
import os
from ipywidgets import interact, interactive
import ipywidgets as ipyw
from IPython.display import display
import ipywe.fileselector
from . import wizard as wiz
from .Form import FormFactory

def powderexp(context=None):
    context = context or wiz.Context()
    from .user import getEmailFromConfig, Step_Email
    email = getEmailFromConfig()
    if not email:
        class Step00(Step_Email):
            def nextStep(self):
                nextstep = Step0_SelectBeam(self.context)
                nextstep.show()
                return
        start = Step00(context)
    else:
        context.email = email
        start = Step0_SelectBeam(context)
    start.show()
    return context


class Step0_SelectBeam(wiz.Step_SelectDir):

    header_text = "Please select the directory where the simulated beam was saved"
    instruction = 'Select beam directory'
    context_attr_name = 'beamdir'
    target_name = 'beam'
    def createNextStep(self):
        return Step1_Sample_selector(self.context)
    def validate(self):
        if not super(Step0_SelectBeam, self).validate(): return False
        dir = self.getSelectedDir()
        if not os.path.exists(os.path.join(dir, 'out')):
            self.updateStatusBar("%s: missing subdir 'out'"%dir)
            return False        
        if not os.path.exists(os.path.join(dir, 'out', 'props.json')):
            self.updateStatusBar("%s: missing file 'out/props.json'"%dir)
            return False
        return True
            

class Step1_Sample_selector(wiz.Step_SelectDir):
    header_text = "Please select the directory where a sample assembly was saved"
    instruction = 'Select sample assembly directory'
    context_attr_name = 'sampleassembly_dir'
    target_name = 'sample-assembly'
    def createNextStep(self):
        return Step2_Workdir(self.context)
    def validate(self):
        if not super(Step1_Sample_selector, self).validate(): return False
        dir = self.getSelectedDir()
        if not os.path.exists(os.path.join(dir, 'sampleassembly.xml')):
            self.updateStatusBar("%s: missing 'sampleassembly.xml'"%dir)
            return False        
        return True
    pass


class Step2_Workdir(wiz.Step_SelectDir):
    header_text = "Please select the workding directory for your simulation"
    instruction = 'Select working directory'
    context_attr_name = 'work_dir'
    target_name = 'working'
    newdir = True
    def createNextStep(self):
        return Step3_Sim_Params(self.context)
    pass


class SimFF(FormFactory):

    P = FormFactory.P
    parameters = [
        # P(name='type', label="Instrument type", widget=ipyw.Text("DGS")),
        P(name='instrument_name', label="Instrument name", choices=['ARCS', 'SEQUOIA', 'CNCS']),
        P(name='ncount', label="Neutron count", widget=ipyw.Text("1e8"), converter=lambda x: int(float(x))),
        P(name="nodes", label="Number of cores", range=(1,20)),
        P(name='buffer_size', label="Neutron buffer size", choices=["1e6", "1e7"], converter=lambda x: int(float(x))),
        P(name='Qaxis', label="Qaxis (Qmin Qmax dQ). unit: inverse angstrom", widget=ipyw.Text("0 15 0.1"), converter=lambda x: map(float, x.split())),
    ]

class Step3_Sim_Params(wiz.Step):
    
    def createBody(self):
        self.form_factory = SimFF()
        form = self.form_factory.createForm()
        widgets= [form]
        return ipyw.VBox(children=widgets)

    def validate(self):
        params = self.form_factory.inputs
        # check user input
        if not params:
            self.updateStatusBar("Please check your inputs")
            return False
        self.context.params = params # save user input
        return True
    
    def createNextStep(self):
        return Step4_Confirm(self.context)

    pass


class Step4_Confirm(wiz.Step):

    def createHeader(self):
        return ipyw.HTML("<h4>Confirmation</h4>")
    
    def createBody(self):
        params = self.context.params
        labels = []; values = []
        for k, v in params.items():
            labels.append(k)
            values.append(str(v))
            continue
        labels.append("Working dir"); values.append(self.context.workdir)
        labels_html = ipyw.HTML("\n".join("<p>%s</p>" % l for l in labels))
        values_html = ipyw.HTML("\n".join("<p>%s</p>" % l for l in values))
        info = ipyw.HBox(children=[labels_html, values_html], layout=ipyw.Layout(padding="5px", border="1px inset #eee"))
        info.add_class("info")
        panel = ipyw.VBox(children=[info])
        return panel

    def validate(self):
        return True

    def nextStep(self):
        return self.generate()
    
    def simulate(self):
        params = self.context.params
        print (params)
        return


# End of file 
