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
        dir = self.getSelectedDir()
        if not os.path.exists(os.path.join(dir, 'out')):
            self.updateStatusBar("%s: missing subdir 'out'"%dir)
            return False        
        if not os.path.exists(os.path.join(dir, 'out', 'props.json')):
            self.updateStatusBar("%s: missing file 'out/props.json'"%dir)
            return False
        return True
            

class Step1_Sample_selector(wiz.Step_SingleChoice):

    header_text = "Sample selector"
    choices = ['Choose a sample directory', 'Choose from templates']
    
    def createNextStep(self):
        next_step = "Step2_" + self.select.value.replace(' ', '_')
        next_step = eval(next_step)
        return next_step(self.context)
    

class Step2_Choose_a_sample_directory(wiz.Step_SelectDir):
    header_text = "Please select the directory where a sample assembly was saved"
    instruction = 'Select sample assembly directory'
    context_attr_name = 'sampleassembly_dir'
    target_name = 'sample-assembly'
    def createNextStep(self):
        return Step3_Sample_selector(self.context)
    def validate(self):
        dir = self.getSelectedDir()
        if not os.path.exists(os.path.join(dir, 'sampleassembly.xml')):
            self.updateStatusBar("%s: missing 'sampleassembly.xml'"%dir)
            return False        
        return True
    pass


class Step2_Choose_from_templates(wiz.Step):
    pass


class Step3_Sim_Params(wiz.Step):
    pass

# End of file 
