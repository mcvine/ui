# -*- Python -*-
#
# Jiao Lin <jiao.lin@gmail.com>
#

from __future__ import print_function
import os
import ipywidgets as ipyw
from . import wizard as wiz
from .Form import FormFactory

def beam(context=None):
    context = context or wiz.Context()
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
        P(name='ncount', label="Neutron count", widget=ipyw.Text("1e8"), converter=lambda x: int(float(x))),
        P(name="nodes", label="Number of cores", range=(1,20)),
    ]
    
    def createHelpText(self):
        return ipyw.HTML("""<div>
Click <a target="_blank" href="https://github.com/mcvine/ui/wiki/DGS-instrument-beam-simulation-parameters">here</a> for explanations
of parameters.
</div>""")


class ARCS(DGS):

    P = FormFactory.P
    parameters = DGS.parameters + [
        # P(name='emission_time', label="Emission time", widget=ipyw.Text("-1."), converter=float),
        P(name="fermi_chopper", label="Fermi chopper", choices=['100-1.5-SMI', '700-1.5-SMI', '700-0.5-AST']),
        P(name="fermi_nu", label="Fermi chopper frequency", choices=[600., 480., 360., 300.]),
        P(name="T0_nu", label="T0 chopper frequency", choices=["60.", "90.", "120."], converter=float),
        P(name="with_moderator_angling", default=True),
    ]
    
        
class SEQUOIA(DGS):

    P = FormFactory.P
    parameters = DGS.parameters + [
        # P(name='emission_time', label="Emission time", widget=ipyw.Text("-1."), converter=float),
        P(name="fermi_chopper", label="Fermi chopper", choices=['100-2.03-AST', '700-3.56-AST','700-0.5-AST']),
        P(name="fermi_nu", label="Fermi chopper frequency", choices=[600., 480., 360., 300.]),
        P(name="T0_nu", label="T0 chopper frequency", choices=["60.", "90.", "120."], converter=float),
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


class Step0_Instrument(wiz.Step):

    def createHeader(self):
        return ipyw.HTML("<h4>Choose instrument</h4>")

    def createBody(self):
        self.select = ipyw.Dropdown(
            options=['ARCS', 'SEQUOIA', 'CNCS', "HYSPEC"], value='ARCS', description='Insturment:')
        widgets= [self.select]
        return ipyw.VBox(children=widgets)

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

    def createHeader(self):
        return ipyw.HTML("<h4>Beam configuration for %s</h4>" % self.context.instrument)
    
    def createBody(self):
        self.form_factory = eval(self.context.instrument)()
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
        self.context.params = params # save user input
        return True
    
    def createNextStep(self):
        return Step2_Outdir(self.context)


class Step2_Outdir(wiz.Step_SelectDir):
    header_text = "Output directory"
    instruction = 'Select output directory'
    context_attr_name = 'outdir'
    target_name = 'output'
    newdir = True
    
    def createNextStep(self):
        return Step3_Confirm(self.context)


class Step3_Confirm(wiz.Step):

    def createHeader(self):
        return ipyw.HTML("<h4>Confirmation</h4>")
    
    def createBody(self):
        labels = ["Instrument"]; values = [self.context.instrument]
        params = self.context.params
        for k, v in params.items():
            labels.append(k)
            values.append(str(v))
            continue
        labels.append("Output dir"); values.append(self.context.outdir)
        labels_html = ipyw.HTML("\n".join("<p>%s</p>" % l for l in labels))
        values_html = ipyw.HTML("\n".join("<p>%s</p>" % l for l in values))
        info = ipyw.HBox(children=[labels_html, values_html], layout=ipyw.Layout(padding="5px", border="1px inset #eee"))
        info.add_class("info")
        self.confirm = ipyw.Checkbox(value=False, description="Everything is good. Run simulation")
        widgets = [info, self.confirm]
        #
        if os.listdir(self.context.outdir):
            self.confirm_rmtree = ipyw.Checkbox(value=False, description="Removing all files in %s. Are you sure?" % self.context.outdir)
            widgets.append(self.confirm_rmtree)
        else:
            self.confirm_rmtree = None
        panel = ipyw.VBox(children=widgets)
        return panel

    def validate(self):
        if not self.confirm.value:
            return False # not confirmed, cannot proceed
        if self.confirm_rmtree is not None:
            # directory is not empty
            if not self.confirm_rmtree.value: return False # not confirmed to remove everything, cannot proceed
            # remove everything
            import shutil
            shutil.rmtree(self.context.outdir)
            # create the empty dir
            os.makedirs(self.context.outdir)
        return True

    def nextStep(self):
        return simulate(self.context)
    

def simulate(context, dry_run=False):
    params = context.params
    cmd = 'cd ' + context.outdir + '; mcvine instruments ' + context.instrument.lower() + " beam"
    for k, v in params.items(): cmd += ' --%s=%r' % (k,v)
    logout = "%s/log.sim" % context.outdir
    cmd += ">%s 2>&1" % logout
    context.cmd = cmd
    if dry_run:
        BOLD = '\033[1m'
        UNBOLD = '\033[0m'
        print("** %sThis is a dry run.%s" % (BOLD, UNBOLD))
        print("** The following command will be run if it is not a dry run")
        print("")
        print(' '*4 + cmd)
        status = "dry_run"
        print('\n')
    else:
        print("* Running simulation at %s..." % context.outdir)
        print("  -- Cmd: %s" % cmd)
        print("  -- Please wait...")
        # email
        status = 'running'; notify(context.email, status, context)
        rt = os.system(cmd)
        status = "failed" if rt else "succeeded"
        print("* Your simulation %s" % status)
        #
        print("  -- Logging of simulation is available at %s" % logout)
    # email
    notify(context.email, status, context)
    return
    

def notify(email, status, context):
    params = context.__dict__
    body = notifications[status].format(**params)
    from .utils import notify
    notify(email, 'mcvine simulation %s' % status, params, notifications[status])
    return

notifications = dict(
    dry_run = 'Dry-run: simulation of "{instrument}" beam.',
    succeeded = 'Your simulation of "{instrument}" beam finished successfully in "{outdir}".',
    failed = 'Your simulation of "{instrument}" beam failed in "{outdir}".',
    running = 'Your simulation of "{instrument}" beam is now running in "{outdir}".',
    )

# End of file 
