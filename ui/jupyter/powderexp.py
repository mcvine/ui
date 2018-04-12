# -*- Python -*-
#
# Jiao Lin <jiao.lin@gmail.com>
#


"""
* Choose beam directory
* Choose sample yaml file
* Choose work directory
* Choose simulation parameters
  - ncount
  - nodes
* Generate the simulate folder, and give instructions

"""

from __future__ import print_function
import os
import ipywidgets as ipyw
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
    context_attr_name = 'beam_dir'
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
            

class Step1_Sample_selector(wiz.Step_SelectFile):
    header_text = "Please select the yaml file for the sample"
    instruction = 'Select sample'
    context_attr_name = 'sample_yaml'
    target_name = 'sample yaml'
    def createNextStep(self):
        return Step2_Workdir(self.context)
    def validate(self):
        if not super(Step1_Sample_selector, self).validate(): return False
        path = self.getSelectedFile()
        if not os.path.exists(path):
            self.updateStatusBar("%s: does not exist"%path)
            return False
        from mcvine.workflow.sample import loadSampleYml
        try:
            sample = loadSampleYml(path)
        except Exception as exc:
            self.updateStatusBar("Failed to load sample from %r: \n%s"%(path, exc))
            return False
        self.context.sample_yaml = path
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
        # P(name='Qaxis', label="Qaxis (Qmin Qmax dQ). unit: inverse angstrom", widget=ipyw.Text("0 15 0.1"), converter=lambda x: map(float, x.split())),
    ]

class Step3_Sim_Params(wiz.Step):

    def createHeader(self):
        return ipyw.HTML("<h4>Simulation parameters</h4>")
    
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
        # save user input
        for k, v in params.items():
            setattr(self.context, k, v)
        return True
    
    def createNextStep(self):
        return Step4_Confirm(self.context)

    pass


class Step4_Confirm(wiz.Step):

    def createHeader(self):
        return ipyw.HTML("<h4>Confirmation</h4>")
    
    def createBody(self):
        labels = ['Beam path', 'Sample path', 'Workding directory']
        values = [self.context.beam_dir, self.context.sample_yaml, self.context.work_dir]
        params = [p.name for p in SimFF.parameters]
        for k in params:
            labels.append(k)
            v = getattr(self.context, k)
            values.append(str(v))
            continue
        labels_html = ipyw.HTML("\n".join("<p>%s</p>" % l for l in labels))
        values_html = ipyw.HTML("\n".join("<p>%s</p>" % l for l in values))
        info = ipyw.HBox(children=[labels_html, values_html], layout=ipyw.Layout(padding="5px", border="1px inset #eee"))
        info.add_class("info")
        widgets = [info]
        #
        if os.listdir(self.context.work_dir):
            self.confirm = ipyw.Checkbox(value=False, description="Removing all files in %s. Are you sure?" % self.context.work_dir)
            widgets.append(self.confirm)
        else:
            self.confirm = None
        #
        panel = ipyw.VBox(children=widgets)
        return panel

    def validate(self):
        return self.confirm.value if self.confirm is not None else True

    def nextStep(self):
        return self.generate()
    
    def generate(self):
        params = {}
        for k,v in self.context.iter_kvpairs():
            if k=='email': continue
            params[k] = v
        create_project(**params)
        self.print_instructions()
        return

    def print_instructions(self):
        print(instructions.format(work=self.context.work_dir))

    pass


instructions = """
The simulation scripts and input files are now created in "{work}".
Please examine the files and make modifications if you see fit.
"""

def create_project(
        beam_dir='beam', sample_yaml='sample.yaml', work_dir='work',
        ncount=int(1e8), buffer_size=int(1e6), nodes=10,
        # Qaxis=[0.0, 15.0, 0.1],
        instrument_name='ARCS'):
    type = 'DGS'
    work = os.path.abspath(work_dir)
    import shutil
    if os.path.exists(work):
        shutil.rmtree(work)
    cmd = 'mcvine workflow powder --type {type} --instrument {instrument_name} '
    cmd += '--sample=V --workdir {work} --ncount {ncount} --buffer_size {buffer_size} '
    cmd += '--nodes {nodes} '  # --qaxis "{Qaxis[0]} {Qaxis[1]} {Qaxis[2]}"'
    cmd = cmd.format(**locals())
    if os.system(cmd):
        raise RuntimeError("%s failed" % cmd)
    # beam
    shutil.rmtree(os.path.join(work, 'beam'))
    os.symlink(beam_dir, os.path.join(work, 'beam'))
    # sample
    sa_dir = os.path.join(work, 'sampleassembly')
    shutil.rmtree(sa_dir)
    from mcvine.workflow.sample import loadSampleYml
    sample = loadSampleYml(sample_yaml)
    from mcvine.workflow.sampleassembly.scaffolding import createSampleAssembly
    createSampleAssembly(sa_dir, sample)
    return


def run(context):
    cmd = "cd %s; make" % context.work_dir
    status_file = os.path.join(context.work_dir, 'STATUS')
    with open(status_file, 'wt') as f: f.write('running')
    if os.system(cmd):
        status = "failed"
    else:
        status = 'finished'
    with open(status_file, 'wt') as f: f.write(status)
    notify(context.email, status, context)
    return


def notify(email, status, context):
    params = context.__dict__
    body = notifications[status].format(**params)
    from .utils import sendmail
    try:
        sendmail(
            "mcvine.neutron@gmail.com", email,
            subject="mcvine simulation done", body=body
            )
    except Exception as e:
        import warnings
        warnings.warn(str(e))
        return
    return

notifications = dict(
    finished = "Your simulation of {instrument_name} powder experiment was finished in {work_dir}.",
    failed = "Your simulation of {instrument_name} powder experiment failed in {work_dir}.",
    )

# End of file 
