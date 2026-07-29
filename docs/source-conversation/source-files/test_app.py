from __future__ import annotations

import io
import sqlite3
import unittest
from urllib.parse import urlencode

import app


class StoryGraphAppTests(unittest.TestCase):
    def call(self, path="/", method="GET", query="", form=None):
        output = {}

        def start_response(status, headers):
            output["status"] = status
            output["headers"] = dict(headers)

        body = b""
        if form is not None:
            body = urlencode(form).encode("utf-8")

        environ = {
            "PATH_INFO": path,
            "REQUEST_METHOD": method,
            "QUERY_STRING": query,
            "CONTENT_LENGTH": str(len(body)),
            "CONTENT_TYPE": "application/x-www-form-urlencoded",
            "wsgi.input": io.BytesIO(body),
        }
        payload = b"".join(app.application(environ, start_response))
        output["body"] = payload.decode("utf-8")
        return output

    def test_dashboard(self):
        result = self.call("/")
        self.assertEqual(result["status"], "200 OK")
        self.assertIn("Author Command Center", result["body"])
        self.assertIn("BOOK-3-CANON-v2.0", result["body"])

    def test_scene_detail(self):
        result = self.call("/scenes", query="id=B03-C17-S04")
        self.assertEqual(result["status"], "200 OK")
        self.assertIn("B03-C17-S04", result["body"])
        self.assertIn("Margot", result["body"])
        self.assertIn("Emitter", result["body"])

    def test_search(self):
        result = self.call("/search", query="q=Valerius")
        self.assertEqual(result["status"], "200 OK")
        self.assertIn("Inquisitor Valerius", result["body"])

    def test_knowledge_filter(self):
        result = self.call("/knowledge", query="holder=Margot+Vance")
        self.assertEqual(result["status"], "200 OK")
        self.assertIn("Margot Vance", result["body"])
        self.assertIn("epistemic", result["body"].lower())

    def test_custody_filter(self):
        result = self.call("/custody", query="object=Treaty")
        self.assertEqual(result["status"], "200 OK")
        self.assertIn("Original Integration Treaty", result["body"])

    def test_promise_board(self):
        result = self.call("/promises", query="bucket=FULFILLED")
        self.assertEqual(result["status"], "200 OK")
        self.assertIn("FULFILLED", result["body"])

    def test_continuity_warning(self):
        result = self.call("/continuity", query="bucket=MODEL_LIMITATION_OR_REPAIR")
        self.assertEqual(result["status"], "200 OK")
        self.assertIn("TL-0001", result["body"])
        self.assertIn("not confirmed manuscript errors", result["body"])

    def test_arc_authority_label(self):
        result = self.call("/arcs", query="holder=Jonah")
        self.assertEqual(result["status"], "200 OK")
        self.assertIn("ANALYTICAL_CANON", result["body"])
        self.assertIn("not literal manuscript statements", result["body"])

    def test_revision_proposal_creates_impacts_without_canon_mutation(self):
        conn = app.db()
        before_scenes = conn.execute("SELECT COUNT(*) FROM scenes").fetchone()[0]
        before_props = conn.execute("SELECT COUNT(*) FROM revision_proposals").fetchone()[0]
        conn.close()

        result = self.call(
            "/proposals/new",
            method="POST",
            form={
                "action_id":"ACTION-PROPOSE-SCENE-REVISION",
                "target_type":"scene",
                "target_id":"B03-C17-S04",
                "proposed_change":"Remove the Zippo sabotage.",
                "reason":"Test impact workflow.",
            },
        )
        self.assertEqual(result["status"], "303 See Other")

        conn = app.db()
        after_scenes = conn.execute("SELECT COUNT(*) FROM scenes").fetchone()[0]
        after_props = conn.execute("SELECT COUNT(*) FROM revision_proposals").fetchone()[0]
        proposal = conn.execute(
            "SELECT proposal_id, status FROM revision_proposals ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        impact_count = conn.execute(
            "SELECT COUNT(*) FROM proposal_impacts WHERE proposal_id=?",
            (proposal["proposal_id"],),
        ).fetchone()[0]
        conn.execute("DELETE FROM proposal_events WHERE proposal_id=?", (proposal["proposal_id"],))
        conn.execute("DELETE FROM proposal_impacts WHERE proposal_id=?", (proposal["proposal_id"],))
        conn.execute("DELETE FROM revision_proposals WHERE proposal_id=?", (proposal["proposal_id"],))
        conn.commit()
        conn.close()

        self.assertEqual(before_scenes, after_scenes)
        self.assertEqual(after_props, before_props + 1)
        self.assertEqual(proposal["status"], "READY_FOR_REVIEW")
        self.assertGreater(impact_count, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
