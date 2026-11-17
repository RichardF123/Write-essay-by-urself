"""Synthetic checks for original provenance and independent evaluation splits."""
import copy
from contextlib import closing
import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills' / 'essay-in-your-voice' / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import voice_pairs as pairs
import voice_rag as rag


class PairTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / 'voice.db'
        rag.init_database(self.db, 'writer')
        self.data = {'pairs': []}
        for i, split in enumerate(('train', 'validation', 'test')):
            text = f'I compare {i+2} trees in the {split} orchard.'
            rag.ingest_source(self.db, 'writer', {
                'source_id': split, 'family_id': split, 'role': 'original',
                'authorship': 'confirmed', 'language': 'en', 'genre': 'academic',
                'holdout': split == 'test', 'text': text,
                'whole_text_is_original_narrative': True})
            self.data['pairs'].append({
                'pair_id': split, 'source_id': split, 'start': 0, 'end': len(text),
                'source_sha256': hashlib.sha256(text.encode()).hexdigest(),
                'original': text, 'neutral': f'The comparison covers {i+2} trees in the {split} orchard.',
                'content_contract': ['The number and orchard remain.'], 'topic': 'orchards',
                'split': split, 'protected_literals': [f'{i+2} trees'],
                'review': {k: {'status': 'pass', 'reason': 'Number, setting and comparison retained.'}
                           for k in ('facts', 'conditions', 'causality', 'stance')}})

    def tearDown(self):
        self.tmp.cleanup()

    def validate(self):
        return pairs.validate_dataset(self.data, self.db, 'writer')

    def test_valid_split_and_no_store_mutation(self):
        before = self.db.read_bytes()
        result = self.validate()
        self.assertEqual(result['counts'], {'train': 1, 'validation': 1, 'test': 1})
        self.assertEqual(self.db.read_bytes(), before)

    def test_owner_mismatch(self):
        with self.assertRaisesRegex(ValueError, 'owner'):
            pairs.validate_dataset(self.data, self.db, 'another-writer')

    def test_changed_number(self):
        self.data['pairs'][0]['neutral'] = 'The comparison covers 9 trees.'
        with self.assertRaisesRegex(ValueError, 'numerical'):
            self.validate()

    def test_exponents_are_not_discarded(self):
        self.assertNotEqual(pairs.numbers('The rate is 5e10.'), pairs.numbers('The rate is 5e20.'))
        self.assertNotEqual(pairs.numbers('The rate is 1e-5.'), pairs.numbers('The rate is 1e+5.'))

    def test_neutral_side_cannot_copy_a_test_original(self):
        # Exercise original/neutral overlap with equal numerical inventories.
        import sqlite3
        original = self.data['pairs'][0]['original']
        other = 'We compare 2 trees in a second orchard.'
        with closing(sqlite3.connect(self.db)) as db, db:
            db.execute('UPDATE sources SET text=? WHERE source_id=?', (other, 'validation'))
            db.execute('UPDATE chunks SET start=0,end=? WHERE source_id=?', (len(other), 'validation'))
            h = hashlib.sha256(other.encode()).hexdigest()
            db.execute('UPDATE sources SET snapshot_sha256=? WHERE source_id=?', (h, 'validation'))
        self.data['pairs'][1].update(original=other, end=len(other), source_sha256=h,
                                      neutral=original, protected_literals=[])
        self.data['pairs'][0]['neutral'] = 'The comparison covers 2 trees in the train orchard.'
        with self.assertRaisesRegex(ValueError, 'pair text leaks'):
            self.validate()

    def test_stale_snapshot(self):
        self.data['pairs'][0]['source_sha256'] = 'stale'
        with self.assertRaisesRegex(ValueError, 'stale'):
            self.validate()

    def test_unknown_authorship_and_assisted_revision(self):
        import sqlite3
        for column, value in [('authorship', 'unknown'), ('role', 'assisted_revision')]:
            with closing(sqlite3.connect(self.db)) as db, db:
                db.execute(f'UPDATE sources SET {column}=? WHERE source_id=?', (value, 'train'))
            with self.assertRaisesRegex(ValueError, 'confirmed originals'):
                self.validate()

    def test_holdout_cannot_train(self):
        self.data['pairs'][2]['split'] = 'train'
        with self.assertRaisesRegex(ValueError, 'holdout'):
            self.validate()

    def test_document_family_cannot_leak(self):
        import sqlite3
        with closing(sqlite3.connect(self.db)) as db, db:
            db.execute("UPDATE sources SET family_id='train' WHERE source_id='validation'")
        with self.assertRaisesRegex(ValueError, 'family leaks'):
            self.validate()

    def test_snapshot_cannot_leak_after_relabel(self):
        import sqlite3
        with closing(sqlite3.connect(self.db)) as db, db:
            db.execute("UPDATE sources SET snapshot_sha256=(SELECT snapshot_sha256 FROM sources WHERE source_id='train') WHERE source_id='validation'")
        self.data['pairs'][1]['source_sha256'] = self.data['pairs'][0]['source_sha256']
        with self.assertRaisesRegex(ValueError, 'snapshot leaks'):
            self.validate()

    def test_mixed_genres_require_separate_dataset(self):
        import sqlite3
        with closing(sqlite3.connect(self.db)) as db, db:
            db.execute("UPDATE sources SET genre='notes' WHERE source_id='validation'")
        with self.assertRaisesRegex(ValueError, 'separate datasets'):
            self.validate()

    def test_review_unknown_is_not_pass(self):
        self.data['pairs'][0]['review']['stance']['status'] = 'unknown'
        with self.assertRaisesRegex(ValueError, 'stance'):
            self.validate()

    def test_protected_literal_cannot_be_dropped(self):
        self.data['pairs'][0]['neutral'] = 'The comparison covers 2 plants in the train orchard.'
        with self.assertRaisesRegex(ValueError, 'protected literal'):
            self.validate()

    def test_original_span_cannot_be_replaced(self):
        self.data['pairs'][0]['original'] = 'Another original.'
        with self.assertRaisesRegex(ValueError, 'snapshot mismatch'):
            self.validate()

    def test_missing_test_family(self):
        self.data['pairs'].pop()
        with self.assertRaisesRegex(ValueError, 'distinct train'):
            self.validate()

    def test_outputs_are_not_overwritten(self):
        path = Path(self.tmp.name) / 'result.json'
        pairs.write_new(path, {'first': True})
        with self.assertRaises(FileExistsError):
            pairs.write_new(path, {'first': False})


if __name__ == '__main__':
    unittest.main()
