"""Guard against the prior scope/denominator errors in market-panel assembly."""
import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('hotel_13', Path(__file__).resolve().parents[1]/'src/assemble_hotel_13_market_panel.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def observation(market, value=100):
    return dict(market=market, source_id='test_source', source_url='https://example.com/source',
                observation_period='2025', geography='explicit source boundary', metric='rooms',
                unit='rooms', status='observed', value=value)


class ScopeAndObservationTests(unittest.TestCase):
    def test_missing_measure_stays_in_panel(self):
        MODULE.validate_results([observation('austin', None), observation('paris')], {'austin','paris'})

    def test_missing_extra_or_duplicate_market_is_rejected(self):
        for rows in [[observation('paris')],
                     [observation('paris'), observation('paris')],
                     [observation('paris'), observation('singapore')]]:
            with self.assertRaises(ValueError):
                MODULE.validate_results(rows, {'austin','paris'})

    def test_invalid_quantities_are_not_accepted_as_capacity(self):
        for value in [float('nan'), float('inf'), -1, True, '100 rooms']:
            with self.assertRaises(ValueError):
                MODULE.validate_results([observation('austin',value)], {'austin'})

    def test_source_definition_required(self):
        row = observation('austin')
        row['geography'] = ''
        with self.assertRaises(ValueError):
            MODULE.validate_results([row], {'austin'})


if __name__=='__main__':
    unittest.main()
