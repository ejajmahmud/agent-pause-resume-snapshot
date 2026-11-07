"""Core Agent Pause Resume Snapshot implementation."""
import json
import hmac
import hashlib
import time
from typing import Dict, Any, Optional


class ExecutionSnapshot:
    def __init__(self, session_id: str, step_index: int, state_vars: Dict[str, Any], pending_actions: list):
        self.session_id = session_id
        self.step_index = step_index
        self.state_vars = state_vars
        self.pending_actions = pending_actions
        self.created_at = time.time()

    def serialize(self, secret_key: str) -> str:
        payload = {
            "session_id": self.session_id,
            "step_index": self.step_index,
            "state_vars": self.state_vars,
            "pending_actions": self.pending_actions,
            "created_at": self.created_at
        }
        raw_json = json.dumps(payload, sort_keys=True)
        sig = hmac.new(secret_key.encode("utf-8"), raw_json.encode("utf-8"), hashlib.sha256).hexdigest()
        return json.dumps({"payload": payload, "signature": sig})

    @classmethod
    def deserialize(cls, data_str: str, secret_key: str) -> "ExecutionSnapshot":
        data = json.loads(data_str)
        payload = data["payload"]
        sig = data["signature"]

        raw_json = json.dumps(payload, sort_keys=True)
        expected_sig = hmac.new(secret_key.encode("utf-8"), raw_json.encode("utf-8"), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(sig, expected_sig):
            raise PermissionError("Snapshot signature verification failed: corrupted or tampered state")

        snap = cls(
            session_id=payload["session_id"],
            step_index=payload["step_index"],
            state_vars=payload["state_vars"],
            pending_actions=payload["pending_actions"]
        )
        snap.created_at = payload["created_at"]
        return snap


class AgentSnapshotManager:
    def __init__(self, secret_key: str = "default_agent_secret"):
        self.secret_key = secret_key
        self._snapshots: Dict[str, str] = {}

    def capture(self, session_id: str, step_index: int, state_vars: Dict[str, Any], pending_actions: list) -> str:
        snap = ExecutionSnapshot(session_id, step_index, state_vars, pending_actions)
        serialized = snap.serialize(self.secret_key)
        self._snapshots[session_id] = serialized
        return serialized

    def resume(self, session_id: str) -> ExecutionSnapshot:
        if session_id not in self._snapshots:
            raise KeyError(f"No snapshot found for session {session_id}")
        return ExecutionSnapshot.deserialize(self._snapshots[session_id], self.secret_key)
