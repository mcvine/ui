# -*- Python -*-
#
# Jiao Lin <jiao.lin@gmail.com>
#


"""
Step4: excitation

Excitation config starts with type selection (Step4_ExcitationType).
Then depending on the type, configuration continues.
If {type}.ConfigStart exists, it will start.
Otherwise, Step4a_ExcitationConfig will start.
{type}.ConfigStart could continue with Step4a_ExcitationConfig.
Step4a_ExcitationConfig continue with either {type}.ConfigEnd or Step5_Workdir.

"""

from __future__ import print_function

developer_notes = """
To implement a new excitation,

* implement it in mcvine core
* add yaml support in mcvine.workflow
* add UI support here
"""

import os
import ipywidgets as ipyw
from . import wizard as wiz
from .Form import FormFactory
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


# Excitation type
class Step4_ExcitationType(wiz.Step_SingleChoice):

    def choices(self):
        global excitation_types
        return excitation_types
    def default_choice(self): return 'powderSQE'

    header_text = 'Excitation'
    def createHeader(self):
        return ipyw.HTML("<h3>%s</h3>" % self.header_text)
    
    def validate(self):
        self.context.excitation_type = self.select.value
        return True
    
    def nextStep(self):
        # need to overload this function, since the next step depends on
        # the choice in this step
        self.next_step = next_step = self.createNextStep()
        next_step.previous_step = self
        next_step.show()
        return
                                                                            
    def createNextStep(self):
        return excitation_config_start_step(self.context)

def excitation_config_start_step(context):
    type = context.excitation_type
    try:
        kls = eval("%s.ConfigStart" % type)
    except:
        kls = Step4a_ExcitationConfig
    return kls(context)


# this is the general excitation configuration form if the excitation parameters are simple
class Step4a_ExcitationConfig(wiz.Step):
    
    def createHeader(self):
        return ipyw.HTML("<h4>%s configuration</h4>" % self.context.excitation_type)
    
    def createBody(self):
        self.form_factory = eval(self.context.excitation_type).Excitation()
        self.form_factory.context = self.context
        doc = self.form_factory.createHelpText()
        form = self.form_factory.createForm()
        widgets= [doc, form]
        return ipyw.VBox(children=widgets)

    def validate(self):
        params = self.form_factory.inputs
        # check user input
        if not params:
            self.updateStatusBar("Please check your inputs")
            return False
        if not hasattr(self.context, 'excitation_params'):
            self.context.excitation_params = dict()
        self.context.excitation_params.update(params) # save user input
        return True
    
    def createNextStep(self):
        return excitation_config_end_step(self.context)

    pass

def excitation_config_end_step(context):
    type = context.excitation_type
    from .sample import Step5_Workdir
    try:
        kls = eval("%s.Config_End" % type)
    except:
        kls = Step5_Workdir
    return kls(context)


class Excitation(FormFactory):

    P = FormFactory.P
    parameters = []
    def createHelpText(self): raise NotImplementedError
    pass


from .excitations import powderSQE, phonon_powder_incoherent, powder_analytical_dispersion
excitation_types = ['powderSQE', 'phonon_powder_incoherent', 'powder_analytical_dispersion']

# End of file 
