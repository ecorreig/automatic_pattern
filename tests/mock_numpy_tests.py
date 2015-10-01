__author__ = 'dracks'
try:
    import numpy as np
    import mock_numpy as mnp
    import unittest

    class MockNumPyTest(unittest.TestCase):
        def test_mean(self):
            l=[1,2,3,4,2,3,1,34,34,5,23,23,3,54,23,2,4]
            self.assertEqual(np.mean(l), mnp.mean(l))

        def test_std(self):
            l=[1,2,3,4,2,3,1,34,34,5,23,23,3,54,23,2,4]
            self.assertEqual(np.std(l), mnp.std(l))



except:
    pass