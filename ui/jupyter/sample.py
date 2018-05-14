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
                nextstep = Step1_Packing_Factor(self.context)
                nextstep.show()
                return
        start = Step00(context)
    else:
        context.email = email
        start = Step1_Packing_Factor(context)
    start.show()
    return context


class Step1_Packing_Factor(wiz.Step):
    
    header_text = "Material: packing factor"
    
    def createHeader(self):
        return ipyw.HTML("<h3>%s</h3>" % self.header_text)

    def createBody(self):
        self.packing_factor_text = ipyw.FloatText(value="1.0", description='Packing factor')
        self.body = ipyw.VBox(children=[self.packing_factor_text])
        return self.body

    def validate(self):
        # packing factor
        packing_factor = self.packing_factor_text.value
        if packing_factor <= 0:
            self.updateStatusBar("Packing factor has to be positive")
            return False
        # finalize
        self.context.packing_factor = packing_factor
        return True
    
    def createNextStep(self):
        return Step2_Structure_Interface_Select(self.context)



class Step2_Structure_Interface_Select(wiz.Step_SingleChoice):

    def choices(self):
        return ['import from file', 'manual input']
    
    def default_choice(self): return 'import from file'

    header_text = 'Atomic structure'
    def createHeader(self):
        return ipyw.HTML("<h3>%s</h3>" % self.header_text)
    
    def validate(self):
        self.selected = self.select.value
        return True
    
    def nextStep(self):
        # need to overload this function, since the next step depends on
        # the choice in this step
        self.next_step = next_step = self.createNextStep()
        next_step.previous_step = self
        next_step.show()
        return
                                                                            
    def createNextStep(self):
        n = 'Step2a_Structure_%s' % self.selected.replace(' ', '_')
        Step = eval(n)
        return Step(self.context)


class Step2a_Structure_import_from_file(wiz.Step_SelectFile):
    
    header_text = "Please select the file with atomic structure"
    instruction = 'Select file'
    context_attr_name = 'structure_file'
    target_name = 'Atomic structure file'

    def createHeader(self):
        text = "<h3>%s</h3>" % self.header_text
        text += """
<p>
* Please choose a file with atomic structure file specification.
  Supported file formats are "xyz" and "cif"
<p>
"""
        return ipyw.HTML(text)
    
    def createNextStep(self):
        from .shape import Step3_ShapeType
        return Step3_ShapeType(self.context)
    
    def validate(self):
        if not super(Step2a_Structure_import_from_file, self).validate(): return False
        path = self.getSelectedFile()
        if not os.path.exists(path):
            self.updateStatusBar("%s: does not exist"%path)
            return False
        ext = os.path.splitext(path)[-1]
        if ext not in ['.xyz', '.cif']:
            self.updateStatusBar("%s: file format not supported"%path)
            return False
        from sampleassembly.crystal import ioutils
        conv = getattr(ioutils, '%sfile2unitcell' % ext[1:])
        try:
            structure = conv(path)
        except:
            self.updateStatusBar("Failed to parse file %s" % path)
            return False
        self.context.structure_file = path
        self.context.lattice = None
        return True
    
    pass


def _check_chemical_formula(text):
    # check chemical formula
    from mcvine.workflow.sampleassembly.scaffolding.utils import decode_chemicalformula
    try: formula = decode_chemicalformula(text)
    except Exception as ex:
        raise ValueError("Failed to decode chemical formula.\n" + str(ex))
    if not len(formula):
        raise ValueError("Empty formula")
    s = ''.join('%s%s' % (k,v) for k,v in formula.items())
    if isinstance(s, unicode): s = s.encode()
    return s


class Lattice_abcabg(FormFactory):

    P = FormFactory.P
    parameters = [
        P(name='chemical_formula', label='Chemical formula', widget=ipyw.Text("e.g. V2O3"), converter=_check_chemical_formula),
        P(name='a', label="a", widget=ipyw.FloatText("1.0")),
        P(name='b', label="b", widget=ipyw.FloatText("1.0")),
        P(name='c', label="c", widget=ipyw.FloatText("1.0")),
        P(name='alpha', label="alpha", widget=ipyw.FloatText("90.0")),
        P(name='beta', label="beta", widget=ipyw.FloatText("90.0")),
        P(name='gamma', label="gamma", widget=ipyw.FloatText("90.0")),
    ]

class Step2a_Structure_manual_input(wiz.Step):

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
        self.context.chemical_formula = params['chemical_formula']
        class lattice:
            def totuple(self):
                return (self.a, self.b, self.c, self.alpha, self.beta, self.gamma)
            def __str__(self): return "%s,%s,%s; %s,%s,%s" % self.totuple()
            pass
        self.context.lattice = lattice()
        for k, v in params.items():
            if k == 'chemical_formula': continue
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
        labels = ['name', 'packing_factor', 'atomic structure', 'directory']
        if self.context.lattice:
            atomic_structure = '%s: %s' % (self.context.chemical_formula, self.context.lattice)
        else:
            atomic_structure = self.context.structure_file
        values = [self.context.name, self.context.packing_factor,
                  atomic_structure, self.context.work_dir]
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
        excitation = dict(type = c.excitation_type)
        excitation.update(c.excitation_params)
        shape = {c.shape_type: c.shape_params}
        d = dict(
            name = c.name,
            packing_factor = c.packing_factor,
            excitation = excitation,
            shape = shape,
            temperature = '300*K',
            )
        from diffpy.Structure import Lattice
        if c.lattice:
            lattice_constants = c.lattice.totuple()
            lattice = Lattice(*lattice_constants)
            base = [','.join(list(map(str, v))) for v in lattice.base]
            lattice = dict(
                constants = ','.join(map(str, lattice_constants)),
                basis_vectors = base,
                )
            d['chemical_formula'] = c.chemical_formula
            d['lattice'] = lattice
        else:
            assert c.structure_file
            d['structure_file'] = c.structure_file
        path = os.path.join(c.work_dir, c.name+'.yaml')
        print("writing to %s" % path)
        import yaml
        with open(path, 'w') as outfile:
            yaml.dump(d, outfile, default_flow_style=False)
        return

    pass


# End of file 
