"""CLI for agent-pause-resume-snapshot."""
import sys
import argparse
from .snapshot import AgentSnapshotManager


def main():
    parser = argparse.ArgumentParser(description="Agent Pause Resume Snapshot")
    parser.add_argument("--demo", action="store_true", help="Run demonstration")
    args = parser.parse_args()

    if args.demo:
        mgr = AgentSnapshotManager("demo_key_123")
        serialized = mgr.capture("sess_42", 5, {"files_edited": ["main.py"], "status": "reviewing"}, ["run_tests"])
        print(f"Captured Snapshot: {serialized[:60]}...")
        restored = mgr.resume("sess_42")
        print(f"Restored Snapshot: Step {restored.step_index}, State: {restored.state_vars}")
    else:
        parser.print_help()
    sys.exit(0)


if __name__ == "__main__":
    main()
