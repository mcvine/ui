from . import ExcitationBase, FormFactory, Step4a_ExcitationConfig
import os
import ipywidgets as ipyw
from .. import wizard as wiz

# only need DOS path

class ConfigStart(wiz.Step_SelectFile):
    
    header_text = "Please select the DOS file"
    instruction = 'Select DOS file'
    context_attr_name = 'phonon_powder_incoherent_DOS'
    target_name = 'DOS'

    def __init__(self, *args, **kwds):
        if not os.path.exists('V-dos.idf'):
            cmd = 'wget https://github.com/mcvine/training/raw/master/jui/V-dos.idf'
            if os.system(cmd):
                raise RuntimeError("failed to download V-dos.idf")    
        super(ConfigStart, self).__init__(*args, **kwds)
        return

    def createHeader(self):
        text = "<h3>%s</h3>" % self.header_text
        text += """
<p>
* DOS file: a data file contains phonon density of states. It can be a 2-col ascci (must be *.txt),
or an IDF file (*.idf), or a DOS histogram (*.h5).
<p>
"""
        return ipyw.HTML(text)
    
    def createNextStep(self):
        from ..sample import Step5_Workdir
        return Step5_Workdir(self.context)
    
    def validate(self):
        if not super(ConfigStart, self).validate(): return False
        path = self.getSelectedFile()
        if not os.path.exists(path):
            self.updateStatusBar("%s: does not exist"%path)
            return False
        fn, ext = os.path.splitext(path)
        if ext not in ['.txt', '.h5', '.idf']:
            self.updateStatusBar("%s: not a recognized DOS file"%path)
            return False
        self.context.excitation_params = dict(DOS=path)
        return True
    pass
