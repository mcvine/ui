from . import ExcitationBase, FormFactory, Step4a_ExcitationConfig, validate_range
import os
import ipywidgets as ipyw
from .. import wizard as wiz

class Excitation(ExcitationBase):

    P = FormFactory.P
    parameters = ExcitationBase.parameters + [
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
class ConfigStart(wiz.Step_SelectFile):
    
    header_text = "Please select the powder SQE histogram file"
    instruction = 'Select S(Q,E) file'
    context_attr_name = 'powderSQE_SQEhist'
    target_name = 'SQE histogram file'

    def __init__(self, *args, **kwds):
        if not os.path.exists('uniform-sqe.h5'):
            cmd = 'wget https://github.com/mcvine/training/raw/master/jui/uniform-sqe.h5'
            if os.system(cmd):
                raise RuntimeError("failed to download uniform-sqe.h5")                
        super(ConfigStart, self).__init__(*args, **kwds)
        return

    def createHeader(self):
        text = "<h3>%s</h3>" % self.header_text
        text += """
<p>
* SQE histogram data file: please specify the path to the SQE histogram.
  To see how to create such a histogram, please refer to
<a href="https://github.com/mcvine/ui/wiki/Create-a-powder-S(Q,E)-histogram-file" target="_blank">Create a powder SQE histogram</a>
<p>
"""
        return ipyw.HTML(text)
    
    def createNextStep(self):
        return Step4a_ExcitationConfig(self.context)
    
    def validate(self):
        if not super(ConfigStart, self).validate(): return False
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
