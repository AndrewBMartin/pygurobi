import unittest
import time

import gurobipy as gp
import pygurobi as pg

class PygurobiTestCase(unittest.TestCase):

    def setUp(self):
        self.model = gp.read("forest.lp")
        self.model.ModelSense = -1
        self.model.update()
        self.model.optimize()
    
    def test_simple_functions(self):
        """
        I know it's generally bad practice to test
        multiple units in one test; however, in this
        case all the units are so simple that the
        test is only to call the functions programmatically.
        """

        pg.list_constraints(self.model)
        pg.list_variables(self.model)

        all_vars = pg.get_variables(self.model)
        harv_vars = pg.get_variables(self.model, "harv")
        assert len(harv_vars) == 40
        harv_vars = pg.get_variables(self.model, "ha", approx=True)
        assert len(harv_vars) == 40









