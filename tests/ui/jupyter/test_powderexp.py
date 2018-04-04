#!/usr/bin/env python

def test():
    from mcvine.ui.jupyter import powderexp
    powderexp.create_project()
    powderexp.create_project(instrument_name='SEQUOIA', work_dir='work-seq')
    powderexp.create_project(instrument_name='CNCS', work_dir='work-cncs')
    return


if __name__ == '__main__': test()
