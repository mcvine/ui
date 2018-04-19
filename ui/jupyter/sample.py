# -*- Python -*-
#
# Jiao Lin <jiao.lin@gmail.com>
#


"""
* Material
  * Chemical formula
  * a,b,c,alpha,gamma,beta
* Shape: 
  * type
  * config
* Workdir
* Name:

"""

from __future__ import print_function
import os
import ipywidgets as ipyw
from . import wizard as wiz
from .Form import FormFactory
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


def sample(context=None):
    context = context or wiz.Context()
    from .user import getEmailFromConfig, Step_Email
    email = getEmailFromConfig()
    if not email:
        class Step00(Step_Email):
            def nextStep(self):
                nextstep = Step1_Chemical_formula(self.context)
                nextstep.show()
                return
        start = Step00(context)
    else:
        context.email = email
        start = Step1_Chemical_formula(context)
    start.show()
    return context


class Step1_Chemical_formula(wiz.Step):
    
    header_text = "Material: chemical formula"
    
    def createHeader(self):
        return ipyw.HTML("<h3>%s</h3>" % self.header_text)

    def createBody(self):
        self.chemical_formula_text = ipyw.Text(value="e.g. V2O3", description='Chemical formula')
        self.packing_factor_text = ipyw.FloatText(value="1.0", description='Packing factor')
        self.body = ipyw.VBox(children=[self.chemical_formula_text, self.packing_factor_text])
        return self.body

    def validate(self):
        # formula
        from mcvine.workflow.sampleassembly.scaffolding.utils import decode_chemicalformula
        try: formula = decode_chemicalformula(self.chemical_formula_text.value)
        except Exception as ex:
            self.updateStatusBar("Failed to decode chemical formula.\n" + str(ex))
            return False
        if not len(formula):
            self.updateStatusBar("Empty formula\n")
            return False
        s = ''.join('%s%s' % (k,v) for k,v in formula.items())
        if isinstance(s, unicode): s = s.encode()
        # packing factor
        packing_factor = self.packing_factor_text.value
        if packing_factor <= 0:
            self.updateStatusBar("Packing factor has to be positive")
            return False
        # finalize
        self.context.chemical_formula = s
        self.context.packing_factor = packing_factor
        return True
    
    def createNextStep(self):
        return Step2_Lattice_abcabg(self.context)


class Lattice_abcabg(FormFactory):

    P = FormFactory.P
    parameters = [
        P(name='a', label="a", widget=ipyw.FloatText("1.0")),
        P(name='b', label="b", widget=ipyw.FloatText("1.0")),
        P(name='c', label="c", widget=ipyw.FloatText("1.0")),
        P(name='alpha', label="alpha", widget=ipyw.FloatText("90.0")),
        P(name='beta', label="beta", widget=ipyw.FloatText("90.0")),
        P(name='gamma', label="gamma", widget=ipyw.FloatText("90.0")),
    ]

    
class Step2_Lattice_abcabg(wiz.Step):

    header_text = 'Lattice parameters'
    def createHeader(self):
        return ipyw.HTML("<h3>%s</h3>" % self.header_text)
    
    def createBody(self):
        self.form_factory = Lattice_abcabg()
        form = self.form_factory.createForm(preserve_order=True)
        widgets= [form]
        return ipyw.VBox(children=widgets)

    def validate(self):
        params = self.form_factory.inputs
        # check user input
        if not params:
            self.updateStatusBar("Please check your inputs")
            return False
        # save user input
        class lattice:
            def totuple(self):
                return (self.a, self.b, self.c, self.alpha, self.beta, self.gamma)
            def __str__(self): return "%s,%s,%s; %s,%s,%s" % self.totuple()
            pass
        self.context.lattice = lattice()
        for k, v in params.items():
            setattr(self.context.lattice, k, v)
        return True
    
    def createNextStep(self):
        from .shape import Step3_ShapeType
        return Step3_ShapeType(self.context)

    pass


class Step5_Workdir(wiz.Step_SelectDir):

    header_text = "Please select the directory where the sample will be saved"
    instruction = 'Select workding directory'
    context_attr_name = 'work_dir'
    target_name = 'work'
    newdir = True
    def createNextStep(self):
        return Step6_Name(self.context)
    pass


class Step6_Name(wiz.Step):

    header_text = "Name of the sample"
    
    def createHeader(self):
        return ipyw.HTML("<h3>%s</h3>" % self.header_text)

    def createBody(self):
        self.text = ipyw.Text(value='mysample', description='Name')
        self.body = ipyw.VBox(children=[self.text])
        return self.body

    def validate(self):
        v = self.text.value
        if isinstance(v, unicode): v = v.encode()
        self.context.name = v
        return True
    
    def createNextStep(self):
        return Step7_Confirmation(self.context)

    pass


class Step7_Confirmation(wiz.Step):

    def createHeader(self):
        return ipyw.HTML("<h4>Confirmation</h4>")
    
    def createBody(self):
        labels = ['name', 'chemical_formula', 'packing_factor', 'lattice', 'directory']
        values = [self.context.name, self.context.chemical_formula, self.context.packing_factor,
                  str(self.context.lattice), self.context.work_dir]
        labels_html = ipyw.HTML("\n".join("<p>%s</p>" % l for l in labels))
        values_html = ipyw.HTML("\n".join("<p>%s</p>" % l for l in values))
        info = ipyw.HBox(
            children=[labels_html, values_html],
            layout=ipyw.Layout(padding="5px", border="1px inset #eee"))
        info.add_class("info")

        shape_title = ipyw.HTML("<h4>Shape: %s</h4>" % self.context.shape_type)
        shape_params = self.context.shape_params
        labels = shape_params.keys()
        values = shape_params.values()
        labels_html = ipyw.HTML("\n".join("<p>%s</p>" % l for l in labels))
        values_html = ipyw.HTML("\n".join("<p>%s</p>" % l for l in values))        
        shape_info = ipyw.HBox(
            children=[labels_html, values_html],
            layout=ipyw.Layout(padding="5px", border="1px inset #eee"))
        shape_info.add_class("info")

        excitation_title = ipyw.HTML("<h4>Excitation: %s</h4>" % self.context.excitation_type)
        excitation_params = self.context.excitation_params
        labels = excitation_params.keys()
        values = excitation_params.values()
        labels_html = ipyw.HTML("\n".join("<p>%s</p>" % l for l in labels))
        values_html = ipyw.HTML("\n".join("<p>%s</p>" % (l,) for l in values))        
        excitation_info = ipyw.HBox(
            children=[labels_html, values_html],
            layout=ipyw.Layout(padding="5px", border="1px inset #eee"))
        excitation_info.add_class("info")

        panel = ipyw.VBox(children=[info, shape_title, shape_info, excitation_title, excitation_info])
        return panel

    def validate(self):
        return True

    def nextStep(self):
        return self.generate()
    
    def generate(self):
        c = self.context
        from danse.ins.matter import Lattice
        lattice_constants = c.lattice.totuple()
        lattice = Lattice(*lattice_constants)
        base = [','.join(list(map(str, v))) for v in lattice.base]
        lattice = dict(
            constants = ','.join(map(str, lattice_constants)),
            basis_vectors = base,
            )
        excitation = dict(type = c.excitation_type)
        excitation.update(c.excitation_params)
        shape = {c.shape_type: c.shape_params}
        d = dict(
            name = c.name,
            chemical_formula = c.chemical_formula,
            packing_factor = c.packing_factor,
            lattice = lattice,
            excitation = excitation,
            shape = shape,
            temperature = '300*K',
            )
        path = os.path.join(c.work_dir, c.name+'.yaml')
        print("writing to %s" % path)
        import yaml
        with open(path, 'w') as outfile:
            yaml.dump(d, outfile, default_flow_style=False)
        return

    pass


# End of file 
