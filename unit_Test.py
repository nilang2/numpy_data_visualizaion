# -*- coding: utf-8 -*-

import unittest
import pandas as pd
from pandas.testing import assert_frame_equal
from main import DAV

class TestClass(unittest.TestCase):
    
    def test_csv_to_dataframe(self):
        data = DAV.csv_to_dataframe('data_set.csv')
        self.assertEqual(data, )
    
    def setUp(self):
        try:
            data = pd.read_csv('', sep = ',', header = 0)
        except IOError:
            print('cannot open file')
        self.fixture = data

    def test_dataFrame_constructedAsExpected(self):
        df = pd.DataFrame()
        assert_frame_equal(self.fixture, df)