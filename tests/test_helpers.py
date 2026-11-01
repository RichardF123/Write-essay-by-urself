import importlib.util
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / 'skills' / 'essay-in-your-voice' / 'scripts'


def module(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


scope = module('verify_wording_scope')
history = module('summarize_report_history')


class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.before = '固定\r\nKeep. Edit here. End.'
        start = self.before.index('Edit here.')
        self.start = start
        self.manifest = {'allowed_spans': [{'start': start, 'end': start + 10, 'original': 'Edit here.'}], 'edits': [{'start': start, 'end': start + 10, 'before': 'Edit here.', 'after': 'Rephrase here.'}]}
        self.after = self.before.replace('Edit here.', 'Rephrase here.')

    def test_exact_authorized_replacement_and_unicode(self):
        self.assertTrue(scope.verify(self.before, self.after, self.manifest)['ok'])

    def test_protected_word_or_line_ending_change_is_rejected(self):
        self.assertFalse(scope.verify(self.before, self.after.replace('Keep.', 'Changed.'), self.manifest)['ok'])
        self.assertFalse(scope.verify(self.before, self.after.replace('\r\n', '\n'), self.manifest)['ok'])

    def test_bad_anchor_and_outside_edit_are_rejected(self):
        self.manifest['edits'][0]['before'] = 'wrong'
        self.assertFalse(scope.verify(self.before, self.after, self.manifest)['ok'])
        self.manifest['edits'] = [{'start': 0, 'end': 2, 'before': '固定', 'after': '修改'}]
        self.assertFalse(scope.verify(self.before, self.after, self.manifest)['ok'])

    def test_insertion_at_highlight_boundary_is_rejected(self):
        start = self.start
        self.manifest['edits'] = [{'start': start, 'end': start, 'before': '', 'after': 'New '}]
        candidate = self.before[:start] + 'New ' + self.before[start:]
        self.assertFalse(scope.verify(self.before, candidate, self.manifest)['ok'])

    def test_insertion_inside_highlight_is_accepted(self):
        start = self.start + 4
        self.manifest['edits'] = [{'start': start, 'end': start, 'before': '', 'after': ' now'}]
        candidate = self.before[:start] + ' now' + self.before[start:]
        self.assertTrue(scope.verify(self.before, candidate, self.manifest)['ok'])

    def test_overlapping_edits_are_rejected(self):
        self.manifest['edits'].append(dict(self.manifest['edits'][0]))
        self.assertFalse(scope.verify(self.before, self.after, self.manifest)['ok'])

    def test_stale_source_hash_is_rejected(self):
        self.manifest['before_sha256'] = 'stale'
        self.assertFalse(scope.verify(self.before, self.after, self.manifest)['ok'])


class HistoryTests(unittest.TestCase):
    def report(self, ident, score, **extra):
        return {'report_id': ident, 'submission_id': ident, 'family_id': 'essay-a', 'tool': 'detector', 'score': score, **extra}

    def test_revisions_count_as_one_family_not_training_cases(self):
        result = history.summarize([self.report('one', 46), self.report('two', 45), self.report('three', 38)])
        self.assertEqual(result['independent_document_families'], 1)
        self.assertEqual(result['numeric_observed_range'], [38, 46])
        self.assertIsNone(result['prediction'])

    def test_duplicate_submission_is_not_a_second_run(self):
        one = self.report('one', 38)
        result = history.summarize([one, {**one, 'report_id': 'download-copy'}])
        self.assertEqual(result['unique_submissions'], 1)
        self.assertEqual(result['duplicate_records'], 1)

    def test_suppressed_score_is_not_zero(self):
        result = history.summarize([self.report('one', {'state': 'suppressed', 'below': 20})])
        self.assertIsNone(result['numeric_observed_range'])
        self.assertEqual(result['suppressed_score_observations'], 1)

    def test_same_prose_disagreement_and_censoring(self):
        hidden = self.report('one', {'state': 'suppressed', 'below': 20}, prose_fingerprint='same')
        other = self.report('two', 46, prose_fingerprint='same')
        result = history.summarize([hidden, other])
        self.assertEqual(len(result['same_prose_score_disagreements']), 1)
        other['score'] = 10
        self.assertFalse(history.summarize([hidden, other])['same_prose_score_disagreements'])

    def test_conflicting_duplicate_is_surfaced(self):
        one = self.report('one', 38)
        result = history.summarize([one, {**one, 'score': 45}])
        self.assertEqual(len(result['duplicate_metadata_conflicts']), 1)

    def test_invalid_score_is_rejected(self):
        for score in [True, -1, 101, float('nan'), '*%']:
            with self.assertRaises(ValueError):
                history.summarize([self.report('one', score)])


if __name__ == '__main__':
    unittest.main()
