'''
ad_engine.py

CMSI 485 HW 3: Advertisement engine that selects from two
ad traits to maximize expected utility of converting a sale
for the Forney Industries Protectron 3001

Jackson Myers
'''

from itertools import *
import csv
import unittest
import math
import numpy as np
from pomegranate import *

class AdEngine:

    def __init__(self, data_file, structure, dec_vars, util_map):
        """
        Responsible for initializing the Decision Network of the
        AdEngine from the structure discovered by Tetrad

        :param string data_file: path to csv file containing data on which
        the network's parameters are to be learned
        :param tuple structure: tuple of tuples specifying parental
        relationships between variables in the network; see Pomegranate docs
        for the expected format. Example:
          ((), (0), (1)) represents nodes: [0] -> [1] -> [2]
        :param list dec_vars: list of string names of variables to be
        considered decision points for the agent. Example:
          ["Ad1", "Ad2"]
        :param dict util_map: discrete, tabular, utility map whose keys
        are variables in network that are parents of a utility node, and
        values are dictionaries mapping that variable's values to a utility
        score, e.g.
          {
            "X": {0: 20, 1: -10}
          }
        represents a utility node with single parent X whose value of 0
        has a utility score of 20, and value 1 has a utility score of -10
        """
        self.data_file = data_file
        self.structure = structure
        self.dec_vars = dec_vars
        self.util_map = util_map
        self.names = []

        data = np.genfromtxt(self.data_file, delimiter=",", skip_header=1)
        with open(self.data_file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    self.names = row
                    line_count += 1

        self.decision_network = BayesianNetwork.from_structure(X=data, structure=self.structure, state_names=self.names)
        self.decision_network.bake()

    def decide(self, evidence):
        """
        Given some observed demographic "evidence" about a potential
        consumer, selects the ad content that maximizes expected utility
        and returns a dictionary over any decision variables and their
        best values

        :param dict evidence: dict mapping network variables to their
        observed values, of the format: {"Obs1": val1, "Obs2": val2, ...}
        :return: dict of format: {"DecVar1": val1, "DecVar2": val2, ...}
        """
        best_combo, best_util = None, -math.inf
        # TODO: Rest of the implementation goes here!
        sequence_array = ["".join(seq) for seq in product("01", repeat=len(self.dec_vars))]

        evidence_object = evidence
        for var in self.dec_vars:
            evidence_object[var] = None


        for seq in sequence_array:
            seq_count, util_count = 0, 0
            for var in self.dec_vars:
                evidence_object[var] = int(seq[seq_count])
                seq_count += 1
            for k,v in self.util_map["S"].items():
                util_count += (self.decision_network.predict_proba(X=evidence_object)[7].parameters[0][k]) * v
            if util_count > best_util:
                best_util = util_count
                best_combo = {"Ad1": int(seq[0]), "Ad2": int(seq[1])}

        return best_combo


class AdEngineTests(unittest.TestCase):
    def test_defendotron_ad_engine(self):
        engine = AdEngine(
            data_file = 'hw4_data.csv',
            dec_vars = ["Ad1", "Ad2"],
            # TODO: Current structure is blank; you need to fill this in using
            # the results from the Tetrad analysis!
            structure = ((), (), (0,9), (6,), (0,1), (1,8), (), (2,5), (), ()),
            # TODO: Decide what the utility map should be for the Defendotron
            # example; see format of util_map in spec and above!
            util_map = {
                "S": {0: 0, 1: 5000, 2: 17760}
            }
        )
        self.assertEqual(engine.decide({"G": 0}), {"Ad1": 0, "Ad2": 1})
        self.assertEqual(engine.decide({"F": 1}), {"Ad1": 1, "Ad2": 0})
        self.assertEqual(engine.decide({"G": 1, "T": 0}), {"Ad1": 1, "Ad2": 1})

if __name__ == "__main__":
    unittest.main()
