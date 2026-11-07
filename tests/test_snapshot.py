"""Tests for agent-pause-resume-snapshot."""
import unittest
from agent_pause_resume_snapshot.snapshot import AgentSnapshotManager, ExecutionSnapshot


class TestSnapshot(unittest.TestCase):
    def setUp(self):
        self.mgr = AgentSnapshotManager("test_secret")

    def test_capture_and_restore(self):
        serialized = self.mgr.capture("sess_1", 3, {"counter": 10}, ["tool_a"])
        snap = self.mgr.resume("sess_1")
        self.assertEqual(snap.session_id, "sess_1")
        self.assertEqual(snap.step_index, 3)
        self.assertEqual(snap.state_vars["counter"], 10)

    def test_tamper_detection(self):
        serialized = self.mgr.capture("sess_tamper", 1, {"x": 1}, [])
        tampered = serialized.replace('"x": 1', '"x": 999')
        with self.assertRaises(PermissionError):
            ExecutionSnapshot.deserialize(tampered, "test_secret")
