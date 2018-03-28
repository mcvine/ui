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
import ipywe.wizard as wiz
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


class WizStep(wiz.Step):
    body_layout = ipyw.Layout(border="1px solid lightgray", padding="10px", margin="10px 0px")

    def createPanel(self):
        body = self.createBody()
        # unify layout
        body.layout = self.body_layout
        #
        navigation = self.createNavigation()
        #
        status_bar = self.createStatusBar()
        panel = ipyw.VBox(children=[body, navigation, status_bar])
        return panel

    def createStatusBar(self):
        self.status_bar = ipyw.HTML("")
        return self.status_bar

    def updateStatusBar(self, html):
        self.status_bar.value = html
    

class Step0_SelectBeam(WizStep):

    def createBody(self):
        self.select = ipywe.fileselector.FileSelectorPanel(
            instruction='Select beam directory', start_dir=os.path.expanduser('~'), type='directory',
            next=self.on_sel_beamdir, newdir_toolbar_button=False, stay_alive=True,
        )
        self.body = ipyw.VBox(children=[self.select.panel])
        return self.body

    def on_sel_beamdir(self, selected):
        self.context.beamdir = selected
        text = ipyw.HTML("<p>Selected beam dir: %s</p>" % selected)
        change_button = ipyw.Button(description="Change")
        change_button.on_click(self.on_change_selection)
        self.body.children=[text, change_button]
        return

    def on_change_selection(self, _):
        self.body.children=[self.select.panel]
        return

    def validate(self):
        good = hasattr(self.context, 'beamdir') and \
               self.context.beamdir and \
               os.path.exists(self.context.beamdir) and \
               os.path.isdir(self.context.beamdir)
        if not good:
            self.updateStatusBar("Please select beam directory")
            return False
        return True
    
    def createNextStep(self):
        return
        return Step3_Confirm(self.context)
                                                                            

# End of file 
