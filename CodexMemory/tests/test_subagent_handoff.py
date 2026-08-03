import json
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import subagent_handoff as handoff


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.session = "019fc6ad-d905-71f1-9fbd-77bb9d61ca20"
        self.main_transcript = str(self.root / "main.jsonl")
        Path(self.main_transcript).write_text("", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def event(self, name, **extra):
        data = {
            "hook_event_name": name,
            "session_id": self.session,
            "turn_id": "turn-1",
            "transcript_path": self.main_transcript,
        }
        data.update(extra)
        return data

    def conversation_folder(self):
        idx = handoff.load_index(self.root, self.session)
        return self.root / idx["folder"]

    def test_subagent_start_and_stop_persist_final(self):
        handoff.handle_event(self.event("SessionStart"), self.root)
        handoff.handle_event(
            self.event("UserPromptSubmit", prompt="检查 X3 礼包分类"), self.root
        )
        start = handoff.handle_event(
            self.event("SubagentStart", agent_id="agent-12345678", agent_type="task-checker"),
            self.root,
        )
        self.assertIn("checkpoint", json.dumps(start, ensure_ascii=False))
        agent_transcript = self.root / "agent.jsonl"
        agent_transcript.write_text('{"type":"test"}\n', encoding="utf-8")
        handoff.handle_event(
            self.event(
                "SubagentStop",
                agent_id="agent-12345678",
                agent_type="task-checker",
                agent_transcript_path=str(agent_transcript),
                last_assistant_message="结论：需要人工复核。",
                stop_hook_active=False,
            ),
            self.root,
        )
        record = self.conversation_folder() / "sub-agent" / "task-checker_12345678"
        self.assertEqual("completed", handoff.load_json(record / "state.json")["status"])
        self.assertIn("人工复核", (record / "final-handoff.md").read_text(encoding="utf-8"))
        self.assertTrue((record / "transcript-snapshot.jsonl").is_file())

    def test_side_prompt_and_stop_survive_ephemeral_chat(self):
        handoff.handle_event(self.event("SessionStart"), self.root)
        handoff.handle_event(
            self.event("UserPromptSubmit", prompt="主任务：整理礼包"), self.root
        )
        side_transcript = self.root / "side.jsonl"
        side_transcript.write_text('{"type":"side"}\n', encoding="utf-8")
        response = handoff.handle_event(
            self.event(
                "UserPromptSubmit",
                transcript_path=str(side_transcript),
                prompt="马戏和航海都属于节日礼包",
            ),
            self.root,
        )
        self.assertIn("BTW", json.dumps(response, ensure_ascii=False))
        handoff.handle_event(
            self.event(
                "Stop",
                transcript_path=str(side_transcript),
                last_assistant_message="已记录该分类判断。",
            ),
            self.root,
        )
        records = list((self.conversation_folder() / "BTW").iterdir())
        self.assertEqual(1, len(records))
        self.assertIn("马戏和航海", (records[0] / "user-prompts.md").read_text(encoding="utf-8"))
        self.assertIn("已记录", (records[0] / "checkpoints.md").read_text(encoding="utf-8"))

    def test_main_prompt_receives_unclaimed_handoff(self):
        handoff.handle_event(self.event("SessionStart"), self.root)
        handoff.handle_event(
            self.event("UserPromptSubmit", prompt="主任务：整理礼包"), self.root
        )
        handoff.handle_event(
            self.event("SubagentStart", agent_id="agent-abcdefgh", agent_type="explorer"),
            self.root,
        )
        handoff.handle_event(
            self.event(
                "SubagentStop",
                agent_id="agent-abcdefgh",
                agent_type="explorer",
                agent_transcript_path=None,
                last_assistant_message="发现：航海礼包应归节日礼包。",
                stop_hook_active=False,
            ),
            self.root,
        )
        result = handoff.handle_event(
            self.event("UserPromptSubmit", prompt="继续主任务"), self.root
        )
        self.assertIn("SUBAGENT_HANDOFF_RECOVERY", json.dumps(result, ensure_ascii=False))
        self.assertIn("航海礼包", json.dumps(result, ensure_ascii=False))

    def test_missing_subagent_final_requests_one_more_turn(self):
        handoff.handle_event(self.event("SessionStart"), self.root)
        handoff.handle_event(
            self.event("UserPromptSubmit", prompt="主任务"), self.root
        )
        handoff.handle_event(
            self.event("SubagentStart", agent_id="agent-empty", agent_type="worker"), self.root
        )
        result = handoff.handle_event(
            self.event(
                "SubagentStop",
                agent_id="agent-empty",
                agent_type="worker",
                agent_transcript_path=None,
                last_assistant_message=None,
                stop_hook_active=False,
            ),
            self.root,
        )
        self.assertEqual("block", result["decision"])

    def test_claim_marks_all_records_without_deleting_them(self):
        handoff.handle_event(self.event("SessionStart"), self.root)
        handoff.handle_event(self.event("UserPromptSubmit", prompt="主任务"), self.root)
        handoff.handle_event(
            self.event("SubagentStart", agent_id="agent-claim", agent_type="explorer"), self.root
        )
        old_root = os.environ.get("CODEX_HANDOFF_ROOT")
        os.environ["CODEX_HANDOFF_ROOT"] = str(self.root)
        try:
            args = type("Args", (), {"session_id": self.session})()
            self.assertEqual(0, handoff.cmd_claim(args))
        finally:
            if old_root is None:
                os.environ.pop("CODEX_HANDOFF_ROOT", None)
            else:
                os.environ["CODEX_HANDOFF_ROOT"] = old_root
        record = self.conversation_folder() / "sub-agent" / "explorer_entclaim"
        self.assertTrue(record.is_dir())
        self.assertEqual("claimed", handoff.load_json(record / "state.json")["status"])

    def test_locate_uses_session_index_instead_of_guessing_folder_name(self):
        handoff.handle_event(self.event("SessionStart"), self.root)
        handoff.handle_event(
            self.event("UserPromptSubmit", prompt="标题不会包含完整 session id"), self.root
        )
        expected = self.conversation_folder()
        self.assertNotIn(self.session, expected.name)
        self.assertEqual(
            expected,
            handoff.resolve_conversation_folder(self.root, self.session),
        )

    def test_concurrent_checkpoints_do_not_overwrite(self):
        handoff.handle_event(self.event("SessionStart"), self.root)
        handoff.handle_event(
            self.event("UserPromptSubmit", prompt="主任务"), self.root
        )
        handoff.handle_event(
            self.event("SubagentStart", agent_id="agent-thread", agent_type="worker"), self.root
        )
        record = self.conversation_folder() / "sub-agent" / "worker_ntthread"

        def write_one(number):
            with handoff.ledger_lock(self.root):
                handoff.append_markdown(record / "checkpoints.md", str(number), f"checkpoint-{number}")

        threads = [threading.Thread(target=write_one, args=(i,)) for i in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        text = (record / "checkpoints.md").read_text(encoding="utf-8")
        for i in range(8):
            self.assertIn(f"checkpoint-{i}", text)


if __name__ == "__main__":
    unittest.main()
