import copy
import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'skills' / 'essay-in-your-voice' / 'scripts' / 'summarize_repeated_highlights.py'
spec = importlib.util.spec_from_file_location('repeated', SCRIPT)
repeated = importlib.util.module_from_spec(spec)
spec.loader.exec_module(repeated)


class RepeatedHighlightTests(unittest.TestCase):
    def setUp(self):
        self.data = {
            'family_id': 'synthetic-essay', 'latest_report_id': 'r3',
            'reports': [{'report_id': f'r{i}', 'submission_id': f's{i}', 'draft_id': f'd{i}', 'tool': 'example'} for i in (1, 2, 3)],
            'units': [{'unit_id': 'stable-observation', 'observations': [
                {'report_id': f'r{i}', 'highlight': state, 'mapping': 'exact', 'text': 'A specific observation.', 'locator': 'page 3'}
                for i, state in [(1, 'full'), (2, 'full'), (3, 'none')]
            ]}],
        }

    def result(self):
        return repeated.summarize(self.data)['units'][0]

    def test_twice_then_clear_is_review_history_not_edit_permission(self):
        result = self.result()
        self.assertTrue(result['exactly_requested_count'])
        self.assertFalse(result['review_candidate'])
        self.assertEqual(result['current_edit_permission'], 'not_determined')

    def test_all_three_differs_from_exactly_two(self):
        self.data['units'][0]['observations'][-1]['highlight'] = 'full'
        result = self.result()
        self.assertTrue(result['at_least_requested_count'])
        self.assertFalse(result['exactly_requested_count'])

    def test_unknown_does_not_mean_clear_or_exactly_two(self):
        self.data['units'][0]['observations'].pop()
        result = self.result()
        self.assertEqual(result['unknown_submissions'], 1)
        self.assertIsNone(result['exactly_requested_count'])
        self.assertFalse(result['review_candidate'])

    def test_partial_overlap_does_not_grant_whole_sentence_permission(self):
        self.data['units'][0]['observations'][-1]['highlight'] = 'partial'
        result = self.result()
        self.assertEqual(result['partial_highlight_count'], 1)
        self.assertTrue(result['review_candidate'])
        self.assertEqual(result['current_edit_permission'], 'not_determined')

    def test_duplicate_download_does_not_inflate_counts(self):
        self.data['reports'].append({**self.data['reports'][0], 'report_id': 'download-copy'})
        obs = self.data['units'][0]['observations'][0]
        self.data['units'][0]['observations'].append({**obs, 'report_id': 'download-copy'})
        result = repeated.summarize(self.data)
        self.assertEqual(result['unique_submissions'], 3)
        self.assertEqual(result['duplicate_downloads'], 1)
        self.assertEqual(result['units'][0]['confirmed_highlight_count'], 2)

    def test_conflicting_duplicate_is_rejected(self):
        self.data['reports'].append({**self.data['reports'][0], 'report_id': 'copy'})
        self.data['units'][0]['observations'].append({**self.data['units'][0]['observations'][0], 'report_id': 'copy', 'highlight': 'none'})
        with self.assertRaises(ValueError):
            self.result()

    def test_rewritten_or_merged_unit_does_not_count_as_unchanged(self):
        obs = self.data['units'][0]['observations'][-1]
        obs.update(mapping='merge', text='A joined observation and its explanation.')
        self.assertFalse(self.result()['same_text_across_observed_versions'])

    def test_uncertain_alignment_is_excluded_even_if_color_is_visible(self):
        self.data['units'][0]['observations'][0]['mapping'] = 'uncertain'
        self.assertEqual(self.result()['confirmed_highlight_count'], 1)
        self.assertIsNone(self.result()['exactly_requested_count'])

    def test_invalid_threshold_latest_reference_or_missing_locator_is_rejected(self):
        with self.assertRaises(ValueError):
            repeated.summarize(self.data, True)
        data = copy.deepcopy(self.data)
        data['latest_report_id'] = 'missing'
        with self.assertRaises(ValueError):
            repeated.summarize(data)
        del self.data['units'][0]['observations'][0]['locator']
        with self.assertRaises(ValueError):
            self.result()


if __name__ == '__main__':
    unittest.main()
