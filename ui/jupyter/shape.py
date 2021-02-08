# -*- Python -*-
#
# Jiao Lin <jiao.lin@gmail.com>
#


from __future__ import print_function
import os
import ipywidgets as ipyw
from . import wizard as wiz
from .Form import FormFactory
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


class Step3_ShapeType(wiz.Step_SingleChoice):

    def choices(self):
        return ['sphere', 'block', 'cylinder', 'hollowCylinder', 'sphereShell']
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
        from .excitation import Step4_ExcitationType
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

class Hollowcylinder(Shape):

    P = FormFactory.P
    parameters = Shape.parameters + [
        P(name='in_radius', label="in_radius", widget=ipyw.Text("1.*cm"), converter=str),
        P(name='out_radius', label="out_radius", widget=ipyw.Text("1.1*cm"), converter=str),
        P(name='height', label="height", widget=ipyw.Text("5.*cm"), converter=str),
    ]

class Sphereshell(Shape):

    P = FormFactory.P
    parameters = Shape.parameters + [
        P(name='in_radius', label="in_radius", widget=ipyw.Text("1.*cm"), converter=str),
        P(name='out_radius', label="out_radius", widget=ipyw.Text("1.1*cm"), converter=str),
    ]


# End of file 
