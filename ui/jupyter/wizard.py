from __future__ import print_function
import os
from ipywidgets import interact, interactive
import ipywidgets as ipyw
from IPython.display import display
import ipywe.fileselector
import ipywe.wizard as wiz
from .Form import FormFactory


class WizStep(wiz.Step):
    body_layout = ipyw.Layout(border="1px solid lightgray", padding="10px", margin="10px 0px")

    def createPanel(self):
        header = self.createHeader()
        body = self.createBody()
        # unify layout
        body.layout = self.body_layout
        #
        navigation = self.createNavigation()
        #
        status_bar = self.createStatusBar()
        #
        widgets = []
        if header: widgets.append(header)
        widgets += [body, navigation, status_bar]
        panel = ipyw.VBox(children=widgets)
        return panel

    def createHeader(self): return

    def createStatusBar(self):
        self.status_bar = ipyw.HTML("")
        return self.status_bar

    def updateStatusBar(self, html):
        self.status_bar.value = html
    

class WizStep_SelectDir(WizStep):

    header_text = None
    instruction = None
    context_attr_name = None
    target_name = None

    def start_dir(self): return

    def createHeader(self):
        return ipyw.HTML("<h3>%s</h3>" % self.header_text)

    def createBody(self):
        self.select = ipywe.fileselector.FileSelectorPanel(
            instruction=self.instruction, start_dir=self.start_dir() or os.path.expanduser('~'),
            type='directory',
            next=self.on_sel_dir, newdir_toolbar_button=False, stay_alive=True,
        )
        self.body = ipyw.VBox(children=[self.select.panel])
        return self.body

    def on_sel_dir(self, selected):
        setattr(self.context, self.context_attr_name, selected)
        text = ipyw.HTML("<p>Selected dir: %s</p>" % selected)
        change_button = ipyw.Button(description="Change")
        change_button.on_click(self.on_change_selection)
        self.body.children=[text, change_button]
        return

    def on_change_selection(self, _):
        self.body.children=[self.select.panel]
        return

    def validate(self):
        good = hasattr(self.context, self.context_attr_name)
        if good:
            v = getattr(self.context, self.context_attr_name)
            good = v and os.path.exists(v) and os.path.isdir(v)
        if not good:
            self.updateStatusBar("Please select %s directory" % self.target_name)
            return False
        return True

    def getSelectedDir(self):
        return getattr(self.context, self.context_attr_name)
    

