"""Optional tensor-level checks; run with the existing torch environment."""
import importlib.util
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills' / 'essay-in-your-voice' / 'scripts'))
import voice_steering as steering
HAS_TORCH = importlib.util.find_spec('torch') is not None


class ExtractionTextTests(unittest.TestCase):
    def test_cuda_capacity_gate_accepts_boundary(self):
        steering.require_cuda_capacity(16 * 1024 ** 3, 16)

    def test_cuda_capacity_gate_reports_busy_gpu(self):
        with self.assertRaisesRegex(ValueError, 'Leave unrelated jobs running'):
            steering.require_cuda_capacity(2 * 1024 ** 3, 16)

    def test_cuda_capacity_gate_rejects_invalid_threshold(self):
        for threshold in (-1, float('inf'), float('nan')):
            with self.assertRaisesRegex(ValueError, 'finite and nonnegative'):
                steering.require_cuda_capacity(24 * 1024 ** 3, threshold)

    def test_eos_at_budget_is_a_completed_answer(self):
        self.assertEqual(steering.finish_reason([4, 9], [8, 9], 2), 'eos')

    def test_budget_exhaustion_without_eos_is_truncation(self):
        self.assertEqual(steering.finish_reason([4, 5], 9, 2), 'length')

    def test_empty_output_is_not_eos(self):
        self.assertEqual(steering.finish_reason([], None, 8), 'other')
    def test_pdf_linewraps_do_not_become_style(self):
        original = 'I compare\n two trees. \n'
        self.assertEqual(steering.extraction_text(original, 'collapse-whitespace'),
                         'I compare two trees.')
        self.assertEqual(original, 'I compare\n two trees. \n')

    def test_explicit_raw_mode_preserves_whitespace(self):
        self.assertEqual(steering.extraction_text(' text\n', 'none'), ' text\n')


@unittest.skipUnless(HAS_TORCH, 'Optional backend needs torch')
class SteeringTests(unittest.TestCase):
    def setUp(self):
        import torch
        self.torch = torch
        self.layer = torch.nn.Identity()
        self.x = torch.zeros((1, 3, 4))
        self.v = torch.ones(4)

    def test_zero_installs_no_hook(self):
        with steering.intervention(self.layer, self.v, 0):
            self.assertFalse(self.layer._forward_hooks)
            self.assertTrue(self.torch.equal(self.layer(self.x), self.x))

    def test_only_last_position_changes(self):
        with steering.intervention(self.layer, self.v, 0.5):
            y = self.layer(self.x)
        self.assertTrue(self.torch.equal(y[:, :-1], self.x[:, :-1]))
        self.assertTrue(self.torch.equal(y[:, -1], self.torch.full((1, 4), 0.5)))
        self.assertTrue(self.torch.equal(self.x, self.torch.zeros_like(self.x)))
        self.assertFalse(self.layer._forward_hooks)

    def test_hook_removed_after_failure(self):
        with self.assertRaisesRegex(RuntimeError, 'synthetic'):
            with steering.intervention(self.layer, self.v, 1):
                raise RuntimeError('synthetic')
        self.assertFalse(self.layer._forward_hooks)

    def test_wrong_vector_dimension_rejected(self):
        with self.assertRaisesRegex(ValueError, 'dimension'):
            with steering.intervention(self.layer, self.torch.ones(2), 1):
                self.layer(self.x)
        self.assertFalse(self.layer._forward_hooks)

    def test_tuple_output_keeps_other_fields(self):
        torch = self.torch
        class TupleLayer(torch.nn.Module):
            def forward(self, x):
                return x, 'cache'
        layer = TupleLayer()
        with steering.intervention(layer, self.v, 1):
            y, cache = layer(self.x)
        self.assertEqual(cache, 'cache')
        self.assertTrue(torch.equal(y[:, -1], torch.ones((1, 4))))


if __name__ == '__main__':
    unittest.main()
