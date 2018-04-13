# -*- Python -*-
#
# Jiao Lin <jiao.lin@gmail.com>
#


"""
Step4: excitation

Excitation config starts with type selection (Step4_ExcitationType).
Then depending on the type, configuration continues.
If Step4a_ExcitationConfig_{type}_Start exists, it will start.
Otherwise, Step4a_ExcitationConfig will start.
Step4a_ExcitationConfig_{type}_Start could continue with Step4a_ExcitationConfig.
Step4a_ExcitationConfig continue with either Step4a_ExcitationConfig_{type}_End or Step5_Workdir.
"""

from __future__ import print_function
import os
import ipywidgets as ipyw
from . import wizard as wiz
from .Form import FormFactory
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


# Excitation
class Step4_ExcitationType(wiz.Step_SingleChoice):

    def choices(self):
        return ['powderSQE']
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
        kls = eval("Step4a_ExcitationConfig_%s_Start" % type)
    except:
        kls = Step4a_ExcitationConfig
    return kls(context)


# this is the general excitation configuration form if the excitation parameters are simple
class Step4a_ExcitationConfig(wiz.Step):
    
    def createHeader(self):
        return ipyw.HTML("<h4>%s configuration</h4>" % self.context.excitation_type)
    
    def createBody(self):
        self.form_factory = eval(self.context.excitation_type.capitalize())()
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
        self.context.excitation_params.update(params) # save user input
        return True
    
    def createNextStep(self):
        return excitation_config_end_step(self.context)

    pass

def excitation_config_end_step(context):
    type = context.excitation_type
    from .sample import Step5_Workdir
    try:
        kls = eval("Step4a_ExcitationConfig_%s_End" % type)
    except:
        kls = Step5_Workdir
    return kls(context)


class Excitation(FormFactory):

    P = FormFactory.P
    parameters = []

    def createHelpText(self): raise NotImplementedError

def validate_path(p):
    if not p:
        raise ValueError("Empty")
    p = os.path.abspath(p)
    assert os.path.exists(p)
    assert p.endswith('.h5')
    if isinstance(p, unicode): p = p.encode()
    return p

def validate_range(unit):
    def _to_q(v):
        return '%s*%s' % (v, unit)
    def _(qr):
        qr = eval(qr)
        qr = map(float, qr)
        qr = map(_to_q, qr)
        s =  ','.join(qr)
        if isinstance(s, unicode):
            s = s.encode()
        return s
    return _

class Powdersqe(Excitation):

    P = FormFactory.P
    parameters = Excitation.parameters + [
        # P(name='SQEhist', label="SQE histogram data file", widget=ipyw.Text("uniform-sqe.h5"), converter=validate_path),
        P(name='Qrange', label='Q range. Express it as "Qmin, Qmax". Units: 1./angstrom', widget=ipyw.Text("0.05, 10."), converter=validate_range('1./angstrom')),
        P(name='Erange', label='E range. Express it as "Emin, Emax". Units: meV', widget=ipyw.Text("-48., 48."),  converter=validate_range('meV')),
    ]
    
    def crossCheckInputs(self):
        inputs = self.inputs
        # path = inputs['SQEhist']
        path = self.context.excitation_params['SQEhist']
        import histogram.hdf as hh
        h = hh.load(path)
        # Q
        Q = h.Q
        from pyre.units import parser; parser = parser()
        Qmin, Qmax = parser.parse(inputs['Qrange'])
        AA = parser.parse('angstrom')
        Qmin, Qmax = Qmin*AA, Qmax*AA
        if Qmin <= Q[0]:
            raise ValueError("Qmin too small. should be larger than %s" % Q[0])
        if Qmax >= Q[-1]:
            raise ValueError("Qmax too large. should be less than %s" % Q[-1])
        # E
        E = getattr(h, 'E', None)
        if E is None:
            E = h.energy
        Emin, Emax = parser.parse(inputs['Erange'])
        meV = parser.parse('meV')
        Emin, Emax = Emin/meV, Emax/meV
        if Emin <= E[0]:
            raise ValueError("Emin too small. should be larger than %s" % E[0])
        if Emax >= E[-1]:
            raise ValueError("Emax too large. should be less than %s" % E[-1])
        return

    def createHelpText(self):
        return ipyw.HTML("""<div>
Click <a target="_blank" href="https://github.com/mcvine/ui/wiki/Powder-SQE-kernel">here</a>
for more details on the parameters.
</div>
""")


# specialized step for powderSQE
# the next step is the general configuration step
class Step4a_ExcitationConfig_powderSQE_Start(wiz.Step_SelectFile):
    
    header_text = "Please select the powder SQE histogram file"
    instruction = 'Select S(Q,E) file'
    context_attr_name = 'powderSQE_SQEhist'
    target_name = 'SQE histogram file'

    def __init__(self, *args, **kwds):
        if not os.path.exists('uniform-sqe.h5'):
            cmd = 'wget https://github.com/mcvine/training/raw/master/jui/uniform-sqe.h5'
            if os.system(cmd):
                raise RuntimeError("failed to download uniform-sqe.h5")                
        super(Step4a_ExcitationConfig_powderSQE_Start, self).__init__(*args, **kwds)
        return

    def createHeader(self):
        text = "<h3>%s</h3>" % self.header_text
        text += """
<hr>
<p>
* SQE histogram data file: please specify the path to the SQE histogram.
  To see how to create such a histogram, please refer to
<a href="https://github.com/mcvine/ui/wiki/Create-a-powder-S(Q,E)-histogram-file" target="_blank">Create a powder SQE histogram</a>
<p>
<hr>        
"""
        return ipyw.HTML(text)
    
    def createNextStep(self):
        return Step4a_ExcitationConfig(self.context)
    def validate(self):
        if not super(Step4a_ExcitationConfig_powderSQE_Start, self).validate(): return False
        path = self.getSelectedFile()
        if not os.path.exists(path):
            self.updateStatusBar("%s: does not exist"%path)
            return False
        if not path.endswith('.h5'):
            self.updateStatusBar("%s: not hdf5 file"%path)
            return False
        import histogram.hdf as hh
        try:
            hh.load(path)
        except Exception as exc:
            self.updateStatusBar("Failed to load histogram from %r: \n%s"%(path, exc))
            return False
        self.context.excitation_params = dict(SQEhist=path)
        return True
    pass


# End of file 
