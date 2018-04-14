from . import ExcitationBase, FormFactory, Step4a_ExcitationConfig, validate_range
import os
import ipywidgets as ipyw
from .. import wizard as wiz


def validate_expression(e):
    e = str(e)
    from mcvine.workflow.sampleassembly.scaffolding.powder_analytical_dispersion import check_expression
    check_expression(e)
    return e

class Excitation(ExcitationBase):

    P = FormFactory.P
    parameters = ExcitationBase.parameters + [
        P(name="E_Q", label='E(Q)', value="20.*sin(Q*.4*3.1416)^2", converter=validate_expression),
        P(name="S_Q", label='S(Q)', value="1", converter=validate_expression),
        P(name='Qrange', label='Q range. Express it as "Qmin, Qmax". Units: 1./angstrom', widget=ipyw.Text("0.05, 10."), converter=validate_range('1./angstrom')),
    ]
    
    def createHelpText(self):
        return ipyw.HTML("""<div>
Click <a target="_blank" href="https://github.com/mcvine/ui/wiki/Powder-analytical-dispersion-kernel">here</a>
for more details on the parameters.
</div>
""")
