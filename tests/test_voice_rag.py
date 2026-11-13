"""Synthetic, local-only regression coverage for the personal voice store."""

import copy
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills' / 'essay-in-your-voice' / 'scripts' / 'voice_rag.py'
if not SCRIPT.exists():
    SCRIPT = ROOT / 'scripts' / 'voice_rag.py'
spec = importlib.util.spec_from_file_location('voice_rag', SCRIPT)
rag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rag)


class VoiceRagTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'voice.sqlite3'
        self.owner = 'synthetic-owner'
        rag.init_database(self.path, self.owner)

    def record(self, source_id='essay-a', **changes):
        result = {
            'source_id': source_id, 'family_id': source_id,
            'role': 'original', 'authorship': 'confirmed',
            'language': 'en', 'genre': 'reflection',
            'text': 'The orchard smelled of rain. I paused beside the gate.',
            'whole_text_is_original_narrative': True,
        }
        result.update(changes)
        return result

    def ingest(self, record):
        return rag.ingest_source(self.path, self.owner, record)

    def retrieve(self, query='orchard', **kwargs):
        return rag.retrieve(self.path, self.owner, query, **kwargs)

    def test_only_confirmed_original_non_holdout_sources_supply_voice(self):
        self.ingest(self.record())
        for role in ('assisted_revision', 'report', 'rubric', 'quoted_external', 'draft', 'unknown'):
            self.ingest(self.record(role, role=role))
        self.ingest(self.record('uncertain', authorship='unknown'))
        self.ingest(self.record('held-back', holdout=True))
        hits = self.retrieve(limit=30)['evidence']
        self.assertEqual({hit['source_id'] for hit in hits}, {'essay-a'})

    def test_exact_unicode_crlf_text_and_offsets_are_citable(self):
        text = '前言。\r\n\r\nThe orchard smelled of rain.\r\nI paused.'
        start = text.index('The orchard')
        self.ingest(self.record(text=text, chunks=[{
            'start': start, 'end': len(text), 'functions': ['observation'],
            'locator': 'paragraph 2',
        }]))
        hits = self.retrieve()['evidence']
        self.assertEqual(len(hits), 1)
        hit = hits[0]
        self.assertEqual(hit['text'], text[start:])
        self.assertEqual(text[hit['start']:hit['end']], hit['text'])
        self.assertEqual(hit['snapshot_sha256'], hashlib.sha256(text.encode('utf-8')).hexdigest())
        self.assertEqual(hit['locator'], 'paragraph 2')
        self.assertTrue(hit['chunk_id'])
        self.assertEqual(hit['family_id'], 'essay-a')

    def test_same_family_cannot_supply_multiple_independent_examples(self):
        self.ingest(self.record('version-a', family_id='shared'))
        self.ingest(self.record('version-b', family_id='shared', text='The orchard was quiet in the morning.'))
        self.ingest(self.record('independent', family_id='other', text='I returned to the orchard after school.'))
        hits = self.retrieve(limit=20)['evidence']
        self.assertEqual(len(hits), 2)
        self.assertEqual(len({hit['family_id'] for hit in hits}), len(hits))

    def test_identical_snapshots_cannot_multiply_evidence_under_new_families(self):
        self.ingest(self.record('copy-a', family_id='family-a'))
        self.ingest(self.record('copy-b', family_id='family-b'))
        self.assertEqual(len(self.retrieve(limit=20)['evidence']), 1)

    def test_fts_punctuation_is_treated_as_query_text_without_crashing(self):
        self.ingest(self.record())
        for query in ('"', 'orchard AND (', 'NEAR(', '* : - +', '"orchard'):
            with self.subTest(query=query):
                result = self.retrieve(query)
                self.assertIsInstance(result['evidence'], list)

    def test_short_chinese_query_matches_inside_unsegmented_text(self):
        self.ingest(self.record(text='我走进果园，雨后的泥土散发着清香。', language='zh'))
        hits = self.retrieve('果园', language='zh')['evidence']
        self.assertEqual([hit['source_id'] for hit in hits], ['essay-a'])

    def test_function_retrieval_crosses_topics_without_query_overlap(self):
        text = 'I entered the station before dawn.'
        self.ingest(self.record(text=text, chunks=[{
            'start': 0, 'end': len(text), 'functions': ['scene-opening'],
            'locator': 'opening',
        }]))
        hits = self.retrieve('', functions=['scene-opening'])['evidence']
        self.assertEqual([hit['source_id'] for hit in hits], ['essay-a'])
        self.assertEqual(self.retrieve('', functions=['absent-function'])['evidence'], [])

    def test_metadata_filters_apply_together(self):
        self.ingest(self.record())
        self.ingest(self.record('other-language', language='zh'))
        self.ingest(self.record('other-genre', genre='argument'))
        hits = self.retrieve(language='en', genre='reflection', source_ids=['essay-a'])['evidence']
        self.assertEqual([hit['source_id'] for hit in hits], ['essay-a'])
        self.assertEqual(self.retrieve(source_ids=['nonexistent'])['evidence'], [])

    def test_reingestion_is_idempotent_and_updates_replace_old_evidence(self):
        record = self.record()
        self.assertEqual(self.ingest(record)['status'], 'inserted')
        self.assertEqual(self.ingest(copy.deepcopy(record))['status'], 'unchanged')
        old_hit = self.retrieve()['evidence'][0]
        record['text'] = 'The orchard was silent after the storm.'
        self.assertEqual(self.ingest(record)['status'], 'updated')
        hits = self.retrieve()['evidence']
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]['text'], record['text'])
        self.assertNotEqual(hits[0]['snapshot_sha256'], old_hit['snapshot_sha256'])

    def test_revoking_authorship_removes_previously_eligible_evidence(self):
        record = self.record()
        self.ingest(record)
        record['authorship'] = 'unknown'
        self.ingest(record)
        self.assertEqual(self.retrieve()['evidence'], [])

    def test_forget_removes_source_from_retrieval(self):
        self.ingest(self.record())
        rag.forget_source(self.path, self.owner, 'essay-a')
        self.assertEqual(self.retrieve()['evidence'], [])

    def test_preferences_are_not_presented_as_authored_evidence(self):
        rag.add_preference(self.path, self.owner, 'plain', 'Prefer plain verbs.')
        result = self.retrieve('plain verbs')
        self.assertEqual(result['evidence'], [])
        self.assertTrue(result['preferences'])
        self.assertIn('Prefer plain verbs.', str(result['preferences']))

    def test_owner_mismatch_is_rejected_for_reads_and_mutations(self):
        self.ingest(self.record())
        calls = [
            lambda: rag.init_database(self.path, 'another-owner'),
            lambda: rag.retrieve(self.path, 'another-owner', 'orchard'),
            lambda: rag.ingest_source(self.path, 'another-owner', self.record('foreign')),
            lambda: rag.forget_source(self.path, 'another-owner', 'essay-a'),
            lambda: rag.add_preference(self.path, 'another-owner', 'p', 'text'),
        ]
        for call in calls:
            with self.subTest(call=call), self.assertRaises((ValueError, PermissionError)):
                call()
        self.assertEqual(len(self.retrieve()['evidence']), 1)

    def test_invalid_chunk_offsets_fail_without_polluting_store(self):
        record = self.record(chunks=[{'start': 0, 'end': 9999, 'functions': [], 'locator': 'bad'}])
        with self.assertRaises(ValueError):
            self.ingest(record)
        self.assertEqual(self.retrieve()['evidence'], [])

    def packet_case(self):
        self.ingest(self.record())
        before = 'Protected.\r\nEdit this. End.'
        start = before.index('Edit this.')
        spans = [{'start': start, 'end': start + len('Edit this.'), 'original': 'Edit this.'}]
        packet = rag.build_packet(self.path, self.owner, before, spans, 'orchard')
        manifest = {'allowed_spans': copy.deepcopy(spans), 'edits': [{
            'start': start, 'end': spans[0]['end'], 'before': 'Edit this.', 'after': 'Revise this.',
        }]}
        review = {key: {'status': 'pass', 'reason': 'Synthetic explicit review.'}
                  for key in ('semantics', 'voice', 'reader_facing', 'context')}
        review['voice']['evidence_ids'] = [hit['chunk_id'] for hit in packet['evidence']]
        return packet, before.replace('Edit this.', 'Revise this.'), manifest, review

    def test_authorized_candidate_requires_all_review_gates(self):
        packet, candidate, manifest, review = self.packet_case()
        result = rag.audit_candidate(packet, candidate, manifest, review)
        self.assertTrue(result['scope_ok'])
        self.assertTrue(result['store_current'])
        self.assertTrue(result['ready_for_delivery'])
        for key in ('semantics', 'voice', 'reader_facing', 'context'):
            uncertain = copy.deepcopy(review)
            uncertain[key]['status'] = 'unknown'
            self.assertFalse(rag.audit_candidate(packet, candidate, manifest, uncertain)['ready_for_delivery'])

    def test_audit_rejects_protected_text_and_crlf_changes(self):
        packet, candidate, manifest, review = self.packet_case()
        for changed in (candidate.replace('Protected.', 'Rewritten.'), candidate.replace('\r\n', '\n')):
            result = rag.audit_candidate(packet, changed, manifest, review)
            self.assertFalse(result['scope_ok'])
            self.assertFalse(result['ready_for_delivery'])

    def test_manifest_cannot_expand_packet_edit_authorization(self):
        packet, candidate, manifest, review = self.packet_case()
        manifest['allowed_spans'] = [{'start': 0, 'end': len(packet['before']), 'original': packet['before']}]
        result = rag.audit_candidate(packet, candidate, manifest, review)
        self.assertFalse(result['scope_ok'])
        self.assertFalse(result['ready_for_delivery'])

    def test_voice_review_cannot_cite_nonexistent_evidence(self):
        packet, candidate, manifest, review = self.packet_case()
        review['voice']['evidence_ids'] = ['fabricated-chunk-id']
        self.assertFalse(rag.audit_candidate(packet, candidate, manifest, review)['ready_for_delivery'])

    def test_no_voice_evidence_cannot_be_promoted_to_delivery_ready(self):
        before = 'Keep this.'
        packet = rag.build_packet(self.path, self.owner, before, [], 'unmatched')
        self.assertEqual(packet['evidence'], [])
        review = {key: {'status': 'pass', 'reason': 'Reviewer assertion without examples.'}
                  for key in ('semantics', 'voice', 'reader_facing', 'context')}
        review['voice']['evidence_ids'] = []
        result = rag.audit_candidate(packet, before, {'allowed_spans': [], 'edits': []}, review)
        self.assertFalse(result['ready_for_delivery'])

    def test_corpus_change_or_forgetting_invalidates_prepared_packet(self):
        packet, candidate, manifest, review = self.packet_case()
        self.ingest(self.record(text='The orchard now smelled of smoke.'))
        result = rag.audit_candidate(packet, candidate, manifest, review)
        self.assertFalse(result['store_current'])
        self.assertFalse(result['ready_for_delivery'])
        packet = rag.build_packet(self.path, self.owner, packet['before'], packet['allowed_spans'], 'orchard')
        rag.forget_source(self.path, self.owner, 'essay-a')
        result = rag.audit_candidate(packet, candidate, manifest, review)
        self.assertFalse(result['store_current'])
        self.assertFalse(result['ready_for_delivery'])

    def test_replaced_store_with_same_owner_and_revision_invalidates_packet(self):
        packet, candidate, manifest, review = self.packet_case()
        self.path.unlink()
        rag.init_database(self.path, self.owner)
        self.ingest(self.record(text='The orchard now contains a different account.'))
        result = rag.audit_candidate(packet, candidate, manifest, review)
        self.assertFalse(result['store_current'])
        self.assertFalse(result['ready_for_delivery'])

    def test_mixed_text_requires_explicit_original_spans(self):
        raw = 'Prompt: describe an orchard.\n\nThe orchard smelled of rain.'
        record = self.record(text=raw, whole_text_is_original_narrative=False)
        with self.assertRaises(ValueError):
            self.ingest(record)
        start = raw.index('The orchard')
        record['chunks'] = [{'start': start, 'end': len(raw), 'locator': 'paragraph 2', 'functions': ['observation']}]
        self.ingest(record)
        self.assertEqual(self.retrieve('Prompt')['evidence'], [])
        self.assertEqual(self.retrieve()["evidence"][0]['text'], raw[start:])

    def test_source_metadata_is_returned_without_touching_offsets(self):
        self.ingest(self.record(metadata={'source_locator': 'sample.txt', 'extraction': 'synthetic'}))
        hit = self.retrieve()['evidence'][0]
        self.assertEqual(hit['metadata']['source_locator'], 'sample.txt')

    def test_manifest_stale_hash_is_rejected(self):
        packet, candidate, manifest, review = self.packet_case()
        manifest['before_sha256'] = 'stale'
        self.assertFalse(rag.audit_candidate(packet, candidate, manifest, review)['scope_ok'])


if __name__ == '__main__':
    unittest.main()
