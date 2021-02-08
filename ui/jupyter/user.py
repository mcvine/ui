from __future__ import print_function
import os
import ipywidgets as ipyw
from IPython.display import display
import ipywe.wizard as wiz
import configparser

mcvine_config = os.path.expanduser('~/.mcvine/mcvine.cfg')
def getEmailFromConfig():
    config = configparser.RawConfigParser()
    path = mcvine_config
    if not os.path.exists(path): return
    config.read(path)
    try:
        email = config.get('user', 'email')
    except:
        return
    return email


def saveEmailToConfig(email):
    config = configparser.RawConfigParser()
    try:
        config.add_section('user')
    except configparser.DuplicateSectionError:
        pass
    config.set('user', 'email', email)
    dir = os.path.dirname(mcvine_config)
    if not os.path.exists(dir): os.makedirs(dir)
    with open(mcvine_config, 'ab') as f:
        config.write(f)
    return


class Step_Email(wiz.Step):

    def createPanel(self):
        self.title = title = ipyw.HTML("<h4>Input your email to receive notification of simulation job status</h4>")
        self.text = ipyw.Text(value='', description='Email:')
        OK = ipyw.Button(description='OK')
        OK.on_click(self.handle_next_button_click)
        widgets= [self.title, self.text, OK]
        return ipyw.VBox(children=widgets)

    def validate(self):
        self.context.email = email = self.text.value
        saveEmailToConfig(email)
        return True
    
