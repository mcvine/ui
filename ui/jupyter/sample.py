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
        self.text = ipyw.Text(value="e.g. V2O3", description='Chemical formula')
        self.body = ipyw.VBox(children=[self.text])
        return self.body

    def validate(self):
        from mcvine.workflow.sampleassembly.scaffolding.utils import decode_chemicalformula
        try: formula = decode_chemicalformula(self.text.value)
        except Exception as ex:
            self.updateStatusBar("Failed to decode chemical formula.\n" + str(ex))
            return False
        if not len(formula):
            self.updateStatusBar("Empty formula\n")
            return False
        s = ''.join('%s%s' % (k,v) for k,v in formula.items())
        if isinstance(s, unicode): s = s.encode()
        self.context.chemical_formula = s
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
        return Step3_ShapeType(self.context)

    pass


class Step3_ShapeType(wiz.Step_SingleChoice):

    def choices(self):
        return ['sphere', 'block', 'cylinder']
    def default_choice(self): return 'sphere'

    header_text = 'Shape'
    def createHeader(self):
        return ipyw.HTML("<h3>%s</h3>" % self.header_text)
    
    def validate(self):
        self.context.shape_type = self.select.value
        return True
    
    def nextStep(self):
        # need to overload this function, since the next step depends on
        # the choice in this step
        self.next_step = next_step = self.createNextStep()
        next_step.previous_step = self
        next_step.show()
        return
                                                                            
    def createNextStep(self):
        return Step3a_ShapeConfig(self.context)


class Step3a_ShapeConfig(wiz.Step):
    
    def createHeader(self):
        return ipyw.HTML("<h4>%s configuration</h4>" % self.context.shape_type)
    
    def createBody(self):
        self.form_factory = eval(self.context.shape_type.capitalize())()
        form = self.form_factory.createForm()
        widgets= [form]
        return ipyw.VBox(children=widgets)

    def validate(self):
        params = self.form_factory.inputs
        # check user input
        if not params:
            self.updateStatusBar("Please check your inputs")
            return False
        self.context.shape_params = params # save user input
        return True
    
    def createNextStep(self):
        return Step4_ExcitationType(self.context)

    pass


class Shape(FormFactory):

    P = FormFactory.P
    parameters = []

class Sphere(Shape):

    P = FormFactory.P
    parameters = Shape.parameters + [
        P(name='radius', label="radius", widget=ipyw.Text("1.*cm"), converter=str),
    ]
    
class Cylinder(Shape):

    P = FormFactory.P
    parameters = Shape.parameters + [
        P(name='radius', label="radius", widget=ipyw.Text("1.*cm"), converter=str),
        P(name='height', label="height", widget=ipyw.Text("5.*cm"), converter=str),
    ]
    
class Block(Shape):

    P = FormFactory.P
    parameters = Shape.parameters + [
        P(name='width', label="width", widget=ipyw.Text("1.*cm"), converter=str),
        P(name='height', label="height", widget=ipyw.Text("1.*cm"), converter=str),
        P(name='thickness', label="thickness", widget=ipyw.Text("1.*cm"), converter=str),
    ]
    


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
        return Step4a_ExcitationConfig(self.context)


class Step4a_ExcitationConfig(wiz.Step):
    
    def createHeader(self):
        return ipyw.HTML("<h4>%s configuration</h4>" % self.context.excitation_type)
    
    def createBody(self):
        self.form_factory = eval(self.context.excitation_type.capitalize())()
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
        self.context.excitation_params = params # save user input
        return True
    
    def createNextStep(self):
        return Step5_Workdir(self.context)

    pass


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
        P(name='SQEhist', label="SQE histogram data file", widget=ipyw.Text("uniform-sqe.h5"), converter=validate_path),
        P(name='Qrange', label='Q range. Express it as "Qmin, Qmax". Units: 1./angstrom', widget=ipyw.Text("0.05, 10."), converter=validate_range('1./angstrom')),
        P(name='Erange', label='E range. Express it as "Emin, Emax". Units: meV', widget=ipyw.Text("-48., 48."),  converter=validate_range('meV')),
    ]
    
    def crossCheckInputs(self):
        inputs = self.inputs
        path = inputs['SQEhist']
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
<p>
* SQE histogram data file: please specify the path to the SQE histogram. 
</p>
<p>
To see how to create such a histogram, please refer to 
<a href="https://github.com/mcvine/ui/wiki/Create-a-powder-S(Q,E)-histogram-file">Create a powder SQE histogram</a>
<p>
</div>""")

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
        labels = ['name', 'chemical_formula', 'lattice', 'directory']
        values = [self.context.name, self.context.chemical_formula, str(self.context.lattice), self.context.work_dir]
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
