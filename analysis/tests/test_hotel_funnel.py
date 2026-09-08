import sys
import csv
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from audit_hotel_funnel import is_hotel, compare, ratio, aggregate, pool_results, write_csv, REVIEW_FIELDS
import report_hotel_funnel as report

def row(i,kind='Room in hotel',reviews=5):
    return dict(id=str(i),host_id=str(i),property_type=kind,room_type='Private room',
        number_of_reviews=str(reviews),number_of_reviews_ltm='3',number_of_reviews_l30d='1',
        minimum_nights='1',first_review='2026-01-01')

class HotelFunnelTests(unittest.TestCase):
    def test_taxonomy_keeps_serviced_apartments_separate(self):
        self.assertTrue(is_hotel(row(1,'Room in boutique hotel')))
        self.assertFalse(is_hotel(row(1,'Room in aparthotel')))
        r=row(1,'Room in serviced apartment'); r['room_type']='Hotel room'
        self.assertFalse(is_hotel(r)); self.assertTrue(is_hotel(r,'broad'))
        self.assertFalse(is_hotel(row(1),'boutique'))
    def test_acquisition_reclassification_exit_are_disjoint(self):
        a={'1':row(1),'2':row(2,'Entire home'),'3':row(3),'4':row(4)}
        b={'1':row(1,reviews=9),'2':row(2),'4':row(4,'Entire home'),'5':row(5)}
        r=compare(a,b,'2025-09-01','strict')
        self.assertEqual(r['baseline_listings'],3)
        self.assertEqual(r['endpoint_listings'],3)
        self.assertEqual(r['new_to_panel_hotel_ids'],1)
        self.assertEqual(r['recategorized_into_hotel'],1)
        self.assertEqual(r['recategorized_out_of_hotel'],1)
        self.assertEqual(r['absent_baseline_hotel_ids'],1)
        self.assertEqual(r['retained_lifetime_review_delta_nonnegative'],4)
    def test_empty_market_no_zero_filled_growth(self):
        r=compare({}, {'1':row(1)},'2025-09-01','strict')
        self.assertIsNone(r['listings_growth'])
        self.assertIsNone(ratio(3,0))
    def test_removed_reviews_and_missing_reviews_are_flagged(self):
        a={'1':row(1,reviews=9),'2':row(2)}
        b={'1':row(1,reviews=5),'2':row(2)}; b['2']['number_of_reviews']=''
        r=compare(a,b,'2025-09-01','strict')
        self.assertEqual(r['retained_negative_review_delta_ids'],1)
        self.assertEqual(r['retained_missing_lifetime_review_delta_ids'],1)
        self.assertEqual(r['retained_lifetime_review_delta_nonnegative'],0)

    def test_missing_endpoint_is_unknown_not_a_complete_review_loss(self):
        for field, label in zip(REVIEW_FIELDS, ('ltm', 'l30d')):
            with self.subTest(field=field):
                a = {'1': row(1)}
                b = {'1': dict(a['1'], **{field: ''})}
                r = compare(a, b, '2025-09-01', 'strict')
                self.assertIsNone(r['endpoint_'+field])
                self.assertIsNone(r[field+'_growth'])
                self.assertIsNone(r[label+'_reviews_per_listing_endpoint'])
                self.assertEqual(r['endpoint_'+field+'_observed_sum'], 0)
                self.assertEqual(r['endpoint_'+field+'_missing'], 1)

    def test_partial_reviews_preserve_only_a_labeled_observed_subtotal(self):
        a = {'1': row(1), '2': row(2)}
        b = {'1': row(1), '2': dict(row(2), number_of_reviews_ltm='')}
        r = compare(a, b, '2025-09-01', 'strict')
        self.assertEqual(r['endpoint_number_of_reviews_ltm_observed_sum'], 3)
        self.assertEqual(r['endpoint_number_of_reviews_ltm_missing'], 1)
        self.assertIsNone(r['endpoint_number_of_reviews_ltm'])
        self.assertIsNone(r['number_of_reviews_ltm_growth'])
        self.assertIsNone(r['ltm_reviews_per_listing_endpoint'])
        self.assertEqual(r['number_of_reviews_l30d_growth'], 0)

    def test_missing_baseline_does_not_create_growth(self):
        a = {'1': dict(row(1), number_of_reviews_ltm='')}
        r = compare(a, {'1': row(1)}, '2025-09-01', 'strict')
        self.assertIsNone(r['baseline_number_of_reviews_ltm'])
        self.assertIsNone(r['number_of_reviews_ltm_growth'])
        self.assertEqual(r['endpoint_number_of_reviews_ltm'], 3)

    def test_reported_zero_and_empty_population_remain_zero(self):
        for field in REVIEW_FIELDS:
            with self.subTest(field=field):
                a = {'1': row(1)}
                b = {'1': dict(row(1), **{field: '0'})}
                r = compare(a, b, '2025-09-01', 'strict')
                self.assertEqual(r['endpoint_'+field], 0)
                self.assertEqual(r[field+'_growth'], -1)
                self.assertIsNone(compare(b, a, '2025-09-01', 'strict')[field+'_growth'])
                self.assertEqual(aggregate([])[field], 0)

    def test_pool_missingness_is_order_independent_including_retained_ids(self):
        a = {'1': row(1)}
        gap = dict(scope='strict', pair_eligible=True, **compare(
            a, {'1': dict(row(1), number_of_reviews_ltm='')}, '2025-09-01', 'strict'))
        complete = dict(scope='strict', pair_eligible=True, **compare(a, a, '2025-09-01', 'strict'))
        for rows in ([gap, complete], [complete, gap], [gap, gap]):
            with self.subTest(all_missing=rows == [gap, gap], first_missing=rows[0] is gap):
                p = pool_results(rows, 'strict')
                self.assertEqual(p['markets'], 2)
                self.assertEqual(p['endpoint_listings'], 2)
                for key in ('endpoint_number_of_reviews_ltm', 'retained_number_of_reviews_ltm',
                            'number_of_reviews_ltm_growth', 'ltm_reviews_per_listing_growth',
                            'retained_ltm_reviews_growth'):
                    self.assertIsNone(p[key], key)
                self.assertEqual(p['endpoint_number_of_reviews_ltm_observed_sum'],
                                 sum(r['endpoint_number_of_reviews_ltm_observed_sum'] for r in rows))
                self.assertEqual(p['number_of_reviews_l30d_growth'], 0)
        self.assertEqual(pool_results([gap, complete], 'strict'), pool_results([complete, gap], 'strict'))

    def test_pool_excludes_ineligible_gaps_and_handles_empty_cohorts(self):
        a = {'1': row(1)}
        complete = dict(scope='strict', pair_eligible=True, **compare(a, a, '2025-09-01', 'strict'))
        excluded = dict(scope='strict', pair_eligible=False, **compare(
            a, {'1': dict(row(1), number_of_reviews_ltm='')}, '2025-09-01', 'strict'))
        self.assertEqual(pool_results([complete, excluded], 'strict')['number_of_reviews_ltm_growth'], 0)
        empty = dict(scope='strict', pair_eligible=True, **compare({}, {}, '2025-09-01', 'strict'))
        self.assertIsNone(pool_results([empty], 'strict')['ltm_reviews_per_listing_growth'])
        with self.assertRaisesRegex(ValueError, 'No eligible markets'):
            pool_results([excluded], 'strict')

    def test_csv_preserves_unknown_separately_from_observed_zero(self):
        a = {'1': row(1)}
        r = compare(a, {'1': dict(row(1), number_of_reviews_ltm='')}, '2025-09-01', 'strict')
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)/'panel.csv'
            write_csv(target, [r])
            with target.open(encoding='utf-8', newline='') as handle:
                saved = next(csv.DictReader(handle))
        self.assertEqual(saved['endpoint_number_of_reviews_ltm'], '')
        self.assertEqual(saved['number_of_reviews_ltm_growth'], '')
        self.assertEqual(saved['endpoint_number_of_reviews_ltm_observed_sum'], '0')
        self.assertEqual(saved['endpoint_number_of_reviews_ltm_missing'], '1')

    def test_report_stops_before_writing_a_narrative_over_missing_data(self):
        missing = dict(scope='strict', endpoint_number_of_reviews_ltm_missing='1')
        with tempfile.TemporaryDirectory() as temp, patch.object(report, 'ROOT', Path(temp)), \
                patch.object(report, 'read', return_value=[missing]):
            with self.assertRaisesRegex(ValueError, 'Incomplete review data'):
                report.main()
            self.assertEqual(list(Path(temp).iterdir()), [])
        report.require_complete_review_data([dict(missing, endpoint_number_of_reviews_ltm_missing='0')])

if __name__=='__main__': unittest.main()
