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
    from .user import getEmailFromConfig, Step_Email
    email = getEmailFromConfig()
    if not email:
        class Step00(Step_Email):
            def nextStep(self):
                nextstep = Step0_Instrument(self.context)
                nextstep.show()
                return
        start = Step00(context)
    else:
        context.email = email
        start = Step0_Instrument(context)
    start.show()
    return context


class DGS(FormFactory):

    P = FormFactory.P
    # names must match parameters in "mcvine <instrument> beam" CLI
    parameters = [
        P(name='E', label="Nominal energy", widget=ipyw.Text("100."), converter=float),
        P(name='ncount', label="Neutron count", widget=ipyw.Text("1e7"), converter=lambda x: int(float(x))),
        P(name="nodes", label="Number of cores", range=(1,20)),
    ]


class ARCS(DGS):

    P = FormFactory.P
    parameters = DGS.parameters + [
        P(name='emission_time', label="Emission time", widget=ipyw.Text("-1."), converter=float),
        P(name="fermi_chopper", label="Fermi chopper", choices=['100-1.5-SMI', '700-1.5-SMI', '700-0.5-AST']),
        P(name="fermi_nu", label="Fermi chopper frequency", choices=[600., 480., 360., 300.]),
        P(name="T0_nu", label="T0 chopper frequency", choices=["60.", "120."], converter=float),
        P(name="with_moderator_angling", default=True),
    ]
    
        
class SEQUOIA(DGS):

    P = FormFactory.P
    parameters = DGS.parameters + [
        P(name='emission_time', label="Emission time", widget=ipyw.Text("-1."), converter=float),
        P(name="fermi_chopper", label="Fermi chopper", choices=['100-2.03-AST', '700-3.56-AST','700-0.5-AST']),
        P(name="fermi_nu", label="Fermi chopper frequency", choices=[600., 480., 360., 300.]),
        P(name="T0_nu", label="T0 chopper frequency", choices=["60.", "120."], converter=float),
    ]


CNCS_fluxmode2angle_dict = {
    'high flux': 9.0,
    'intermediate': 4.4,
    'high resolution': 2.0,
}
CNCS_fluxmode2angle = lambda x: CNCS_fluxmode2angle_dict[x]
class CNCS(DGS):

    P = FormFactory.P
    parameters = DGS.parameters + [
        P(name='E', label="Nominal energy", widget=ipyw.Text("5."), converter=float),
        P(name="f1", label="Chopper freq 1", default="60.", converter=float),
        P(name="f2", label="Chopper freq 2", default="60.", converter=float),
        P(name="f3", label="Chopper freq 3", default="60.", converter=float),
        P(name="f41", label="Chopper freq 41", default="300.", converter=float),
        P(name="f42", label="Chopper freq 42", default="300.", converter=float),
        P(name="fluxmode", label="Flux mode",
          choices=["high flux", "intermediate", "high resolution"], converter=CNCS_fluxmode2angle),
    ]


class HYSPEC(DGS):

    P = FormFactory.P
    parameters = DGS.parameters + [
        P(name="fermi_nu", label="Fermi chopper frequency", choices=["180."], converter=float),
        P(name='E', label="Nominal energy", default="20.", converter=float),
        P(name="Emin", label="Minimum incident energy", default="10.", converter=float),
        P(name="Emax", label="Maximum incident energy", default="30.", converter=float),
        P(name="LMS", label = 'monochromator to sample distance. unit: meter', default="1.8", converter=float)
    ]

    def crossCheckInputs(self):
        inputs = self.inputs
        if inputs['Emin'] >= inputs['E']:
            raise ValueError("Minimum incident energy should be smaller than nominal energy")
        if inputs['Emax'] <= inputs['E']:
            raise ValueError("Maximum incident energy should be larger than nominal energy")


wizard_step_body_layout = ipyw.Layout(border="1px solid lightgray", padding="10px", margin="10px 0px")

class Step0_Instrument(wiz.Step):

    def createBody(self):
        self.title = title = ipyw.HTML("<h4>Choose instrument</h4>")
        self.select = ipyw.Dropdown(
            options=['ARCS', 'SEQUOIA', 'CNCS', "HYSPEC"], value='ARCS', description='Insturment:')
        widgets= [self.title, self.select]
        return ipyw.VBox(children=widgets, layout=wizard_step_body_layout)

    def validate(self):
        self.context.instrument = self.select.value
        return True
    
    def createNextStep(self):
        return Step1_Parameters(self.context)
    
    def nextStep(self):
        # need to overload this function, since the next step depends on
        # the choice in this step
        self.next_step = next_step = self.createNextStep()
        next_step.previous_step = self
        next_step.show()
        return
                                                                            
class Step1_Parameters(wiz.Step):

    def createBody(self):
        self.form_factory = eval(self.context.instrument)()
        self.title = title = ipyw.HTML("<h4>Beam configuration for %s</h4>" % self.context.instrument)
        form = self.form_factory.createForm()
        widgets= [title, form]
        return ipyw.VBox(children=widgets, layout=wizard_step_body_layout)

    def validate(self):
        params = self.form_factory.inputs
        # check user input
        if not params:
            print("Please check your inputs")
            return False
        self.context.params = params # save user input
        return True
    
    def createNextStep(self):
        return Step2_Outdir(self.context)

class Step2_Outdir(wiz.Step):
    
    def createBody(self):
        self.select = ipywe.fileselector.FileSelectorPanel(
            instruction='Select output directory', start_dir=os.path.expanduser('~'), type='directory',
            next=self.on_sel_outdir, newdir_toolbar_button=True, stay_alive=True,
        )
        self.body = ipyw.VBox(children=[self.select.panel], layout=wizard_step_body_layout)
        return self.body

    def on_sel_outdir(self, selected):
        self.context.outdir = selected
        text = ipyw.HTML("<p>Selected output dir: %s</p>" % selected)
        change_button = ipyw.Button(description="Change")
        change_button.on_click(self.on_change_selection)
        self.body.children=[text, change_button]
        return

    def on_change_selection(self, _):
        self.body.children=[self.select.panel]
        return

    def validate(self):
        good = hasattr(self.context, 'outdir') and self.context.outdir and os.path.exists(self.context.outdir) and os.path.isdir(self.context.outdir)
        if not good:
            print("Please select output directory")
            return False
        return True
    
    def createNextStep(self):
        return Step3_Confirm(self.context)


class Step3_Confirm(wiz.Step):

    def createBody(self):
        title = ipyw.HTML("<h4>Confirmation</h4>")
        labels = ["Instrument"]; values = [self.context.instrument]
        params = self.context.params
        for k, v in params.items():
            labels.append(k)
            values.append(str(v))
            continue
        labels_html = ipyw.HTML("\n".join("<p>%s</p>" % l for l in labels))
        values_html = ipyw.HTML("\n".join("<p>%s</p>" % l for l in values))
        panel = ipyw.VBox(children=[title, ipyw.HBox(children=[labels_html, values_html])], layout=wizard_step_body_layout)
        return panel

    def validate(self):
        return True

    def nextStep(self):
        return self.simulate()
    
    def simulate(self, dry_run=False):
        params = self.context.params
        cmd = 'cd ' + self.context.outdir + '; mcvine instruments ' + self.context.instrument.lower() + " beam"
        for k, v in params.items(): cmd += ' --%s=%r' % (k,v)
        logout = "%s/log.sim" % self.context.outdir
        cmd += ">%s 2>&1" % logout
        if dry_run:
            print(cmd)
            return
        print("* Running simulation at %s..." % self.context.outdir)
        print("  -- Cmd: %s" % cmd)
        print("  -- Please wait...")
        rt = os.system(cmd)
        status = "failed" if rt else "succeeded"
        print("* Your simulation %s" % status)
        #
        print("  -- Logging of simulation is available at %s" % logout)
        body="Simulation of %s beam %s. Please check log file %s" % (
            self.context.instrument, status, logout)
        from .utils import sendmail
        try:
            sendmail(
                "mcvine.neutron@gmail.com", self.context.email,
                subject="mcvine simulation done", body=body
                )
        except Exception as e:
            import warnings
            warnings.warn(str(e))
            return
        return


# End of file 
