import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from model_hotel_funnel import mix_after, nights_per_signed_property, required_properties, contribution_share, validate_market_scope, available_daily_rooms
from verify_hotel_capacity import hotel_category_sum

class HotelModelTests(unittest.TestCase):
    def test_mix_reconciles_to_explicit_night_counts(self):
        self.assertAlmostEqual(mix_after(.05,.1,.3),6.5/(104.5+6.5))
        self.assertEqual(mix_after(0,.1,.3),0)
        self.assertEqual(mix_after(1,.1,.3),1)
        self.assertIsNone(mix_after(.5,-1,-1))
    def test_zero_activation_cannot_produce_nights(self):
        p=nights_per_signed_property(50,0,.5,.7,.1)
        self.assertEqual(p,0); self.assertIsNone(required_properties(1e6,p))
    def test_timing_halves_first_year_capacity(self):
        full=nights_per_signed_property(50,.8,1,.7,.1)
        self.assertAlmostEqual(nights_per_signed_property(50,.8,.5,.7,.1),full/2)
        self.assertAlmostEqual(full,1022)
    def test_invalid_inputs_fail(self):
        for v in [1.1,-.1,float('nan')]:
            with self.assertRaises(ValueError): mix_after(v,.1,.3)
        with self.assertRaises(ValueError): nights_per_signed_property(-1,1,1,1,1)
    def test_credit_economics_separate_award_and_redemption(self):
        self.assertAlmostEqual(contribution_share(.11,.03,1,.15,.5,1),.005)
        self.assertAlmostEqual(contribution_share(.11,.03,0,.15,1,1),.08)
        self.assertAlmostEqual(contribution_share(.11,.03,1,.15,1,1),-.07)
    def test_scope_rejects_duplicate_or_substituted_markets(self):
        selected=[{'market':str(i)} for i in range(25)]
        validate_market_scope(selected,selected)
        duplicate=selected[:24]+[selected[0]]
        with self.assertRaises(ValueError): validate_market_scope(duplicate,selected)
        with self.assertRaises(ValueError): validate_market_scope(selected[:24]+[{'market':'unexpected'}],selected)
    def test_room_nights_are_not_room_stock(self):
        self.assertEqual(available_daily_rooms(34348,31),1108)
        with self.assertRaises(ValueError): available_daily_rooms(34348,0)
        with self.assertRaises(ValueError): available_daily_rooms(float('nan'),31)
    def test_excluded_accommodation_categories_reconcile(self):
        self.assertEqual(hotel_category_sum(48078,[6589,23507,5874,3686],[4283,4139]),39656)
        with self.assertRaises(ValueError): hotel_category_sum(48078,[6589,23507,5874,3686],[4283,0])
        with self.assertRaises(ValueError): hotel_category_sum(48078,[None],[4283,4139])

if __name__=='__main__': unittest.main()
