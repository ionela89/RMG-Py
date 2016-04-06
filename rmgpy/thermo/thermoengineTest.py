#!/usr/bin/env python
# encoding: utf-8 -*-

"""
This module contains unit tests of the rmgpy.parallel module.
"""

import os
import sys
import unittest
import random

from rmgpy import settings
from rmgpy.data.rmg import RMGDatabase
from rmgpy.rmg.main import RMG
from rmgpy.scoop_framework.framework import TestScoopCommon

from rmgpy.species import Species

try:
    from scoop import futures, _control, shared
except ImportError, e:
    import logging as logging
    logging.debug("Could not properly import SCOOP.")


def load():
    tearDown()
    rmg = RMG()#for solvent
    database = RMGDatabase()
    database.loadThermo(os.path.join(settings['database.directory'], 'thermo'))
    database.loadTransport(os.path.join(settings['database.directory'], 'transport'))

def tearDown():
    """
    Reset the loaded database
    """
    import rmgpy.data.rmg
    rmgpy.data.rmg.database = None

def funcSubmit():
    """
    Test that we can submit a number of species.
    """
    load()

    spcs = [
            Species().fromSMILES('C'),\
            Species().fromSMILES('CC'), \
            Species().fromSMILES('CCC')
            ]
    
    for spc in spcs:
        spc.submit()

    return True

def funcGet():
    """
    Test if we can retrieve thermo of species even before we have submitted them explicitly.
    """
    load()

    spcs = [
            Species().fromSMILES('C'),
            Species().fromSMILES('CC'), \
            Species().fromSMILES('CCC')
            ]
    
    output = []
    for spc in spcs:
        data = spc.getData()
        output.append((spc, data))

    for spc, data in output:
        if not data:
            return False

    return True

def funcSubmitGet():
    """
    Test if we can retrieve thermo of species after submitting some of them.
    """
    load()

    spcs = [
            Species().fromSMILES('C'),\
            Species().fromSMILES('CC'), \
            Species().fromSMILES('CCC')
            ]
    
    for spc in spcs:
        spc.submit()

    absent = Species().fromSMILES('[CH3]')
    data = absent.getData()
    if not data: return False

    present = Species().fromSMILES('CC')
    data = present.getData()
    if not data: return False

    random.shuffle(spcs)
    for spc in spcs:
        data = spc.getData()
        if not data: return False        

    return True


class AsyncThermoTest(TestScoopCommon):

    def __init__(self, *args, **kwargs):
        # Parent initialization
        super(self.__class__, self).__init__(*args, **kwargs)
        
        # Only setup the scoop framework once, and not in every test method:
        super(self.__class__, self).setUp()

    @unittest.skipUnless(sys.platform.startswith("linux"),
                         "test currently only runs on linux")
    def testSubmit(self):
        """
        Test that we can submit a request to generate
        thermo/transport for a number of species.
        """
        result = futures._startup(funcSubmit)
        self.assertEquals(result, True)

    @unittest.skipUnless(sys.platform.startswith("linux"),
                         "test currently only runs on linux")
    def testGet(self):
        """
        Test that we can get the data of a number of species.
        """
        result = futures._startup(funcGet)
        self.assertEquals(result, True)

if __name__ == '__main__' and os.environ.get('IS_ORIGIN', "1") == "1":
    unittest.main()