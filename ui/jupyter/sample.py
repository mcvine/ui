# -*- Python -*-
#
# Jiao Lin <jiao.lin@gmail.com>
#


"""
* Workdir
* Name:
* Shape: 
* Material
  * Chemical formula
  * Unit cell
* Position/orientation
* Sample environment

"""

from __future__ import print_function
import os
from ipywidgets import interact, interactive
import ipywidgets as ipyw
from IPython.display import display
import ipywe.fileselector
from . import wizard as wiz
from .Form import FormFactory

def sampleassembly(context=None):
    context = context or wiz.Context()
    from .user import getEmailFromConfig, Step_Email
    email = getEmailFromConfig()
    if not email:
        class Step00(Step_Email):
            def nextStep(self):
                nextstep = Step1_Workdir(self.context)
                nextstep.show()
                return
        start = Step00(context)
    else:
        context.email = email
        start = Step1_Workdir(context)
    start.show()
    return context


class Step1_Workdir(wiz.Step_SelectDir):

    header_text = "Please select the directory where the sample assembly will be saved"
    instruction = 'Select workding directory'
    context_attr_name = 'work_dir'
    target_name = 'work'
    newdir = True
    def createNextStep(self):
        return Step2_Name(self.context)

    pass

class Step2_Name(wiz.Step):

    header_text = "Name of the sample assembly"
    
    def createHeader(self):
        return ipyw.HTML("<h3>%s</h3>" % self.header_text)

    def createBody(self):
        self.text = ipyw.Text(value='mysample', description='Name')
        self.body = ipyw.VBox(children=[self.select])
        return self.body

    def validate(self):
        return True
    
    def nextStep(self):
        # need to overload this function, since the next step depends on
        # the choice in this step
        self.next_step = next_step = self.createNextStep()
        next_step.previous_step = self
        next_step.show()
        return

    def createNextStep(self):
        raise NotImplementedError

    pass

    

# End of file 
