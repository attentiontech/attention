import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from zipfile import ZipFile

from build import ROOT, build


class PackageContract(unittest.TestCase):
    def test_two_reproducible_formats_share_identity_skill_and_production_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("zipfile.time.localtime", return_value=(2020, 1, 1, 0, 0, 0, 2, 1, 0)):
                first = build()
            self.assertIsInstance(first, tuple, "Build must return Claude and OpenAI archives")
            self.assertEqual(len(first), 2)
            with patch("zipfile.time.localtime", return_value=(2021, 1, 1, 0, 0, 0, 4, 1, 0)):
                second = build(Path(directory) / "second")
            for a, b in zip(first, second):
                self.assertEqual(a.read_bytes(), b.read_bytes())
            with ZipFile(first[0]) as claude, ZipFile(first[1]) as openai:
                self.assertEqual(set(claude.namelist()), {
                    ".claude-plugin/plugin.json", ".mcp.json", "LICENSE", "README.md",
                    "skills/conversations/SKILL.md",
                })
                self.assertEqual(set(openai.namelist()), {
                    "plugin.json", "mcp.json", "LICENSE", "skills/conversations/SKILL.md",
                    "assets/attention-icon.png",
                })
                a = json.loads(claude.read(".claude-plugin/plugin.json"))
                b = json.loads(openai.read("plugin.json"))
                self.assertEqual((a["name"], a["version"]), (b["name"], b["version"]))
                skill = "skills/conversations/SKILL.md"
                self.assertEqual(claude.read(skill), openai.read(skill))
                self.assertEqual(openai.read(skill), (ROOT / skill).read_bytes())
                self.assertNotIn(b"always show them exactly as returned", openai.read(skill))
                self.assertIn(b"summarize", openai.read(skill))
                cm = json.loads(claude.read(".mcp.json"))["mcpServers"]["attention"]
                om = json.loads(openai.read("mcp.json"))["mcpServers"]["attention"]
                self.assertEqual(cm, {"type": "http", "url": "https://api.attention.tech/mcp"})
                self.assertEqual(om["url"], cm["url"])
                self.assertEqual(om["type"], "streamable-http")
                self.assertEqual(om["extensions"]["com.openai"]["auth"], {
                    "type": "oauth", "client": {"mode": "dcr"},
                    "baseScopes": ["mcp:read", "mcp:write"],
                })
                interface = b["extensions"]["com.openai"]["interface"]
                self.assertLessEqual(len(interface["shortDescription"]), 30)
                self.assertIn(interface["logo"].removeprefix("./"), openai.namelist())


if __name__ == "__main__":
    unittest.main()
