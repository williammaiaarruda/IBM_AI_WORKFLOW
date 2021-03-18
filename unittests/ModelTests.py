"""
model tests
"""

import os
import sys
import unittest

sys.path.insert(1, os.path.join('..', os.getcwd()))

# import model specific functions and variables
from model import *


class ModelTest(unittest.TestCase):
    """
    test the essential functionality
    """

    def test_01_train(self):
        """
        test the train functionality
        """

        # train the model
        data_dir = os.path.join("data", "cs-train")
        model_train(data_dir, test=True)
        self.assertTrue(os.path.exists(os.path.join("models", "test-united_kingdom-0_1.joblib")))

    def test_02_load(self):
        """
        test the train functionality
        """

        # train the model
        all_models = model_load()
        print(all_models)
        key = list(all_models.keys())[0]

        self.assertTrue('predict' in dir(all_models[key]))
        self.assertTrue('fit' in dir(all_models[key]))

    def test_03_predict(self):
        """
        test the predict function input
        """

        # ensure that a list can be passed
        query = {'country': 'all',
                 'year': '2020',
                 'month': '01',
                 'day': '05'
                 }
        result = model_predict(query, test=True)
        print(result)
        y_pred = result['y_pred']
        self.assertTrue(y_pred >= -432.4092325822826)


# Run the tests
if __name__ == '__main__':
    unittest.main()
