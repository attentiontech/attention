"""Validate the generated archives offline; report submission inputs separately."""

import argparse
import hashlib
import json
import struct
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlsplit
from zipfile import ZipFile

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(claude_path, openai_path, submission=False):
    with ZipFile(claude_path) as claude, ZipFile(openai_path) as openai:
        shared = {"LICENSE", "skills/conversations/SKILL.md"}
        require(set(claude.namelist()) == shared | {
            ".claude-plugin/plugin.json", ".mcp.json", "README.md",
        }, "Claude archive inventory does not match the package contract")
        require(set(openai.namelist()) == shared | {
            "plugin.json", "mcp.json", "assets/attention-icon.png",
        }, "OpenAI archive inventory does not match the package contract")
        for name in shared:
            require(claude.read(name) == openai.read(name), f"Shared bytes differ: {name}")
        cm = json.loads(claude.read(".claude-plugin/plugin.json"))
        om = json.loads(openai.read("plugin.json"))
        require((cm["name"], cm["version"]) == (om["name"], om["version"]),
                "Package identity or version differs")
        mc = json.loads(openai.read("mcp.json"))
        schema = json.loads((HERE / "schemas/plugin.schema.json").read_text())
        Draft202012Validator(schema).validate(om)
        schema = json.loads((HERE / "schemas/mcp.schema.json").read_text())
        # OpenAI documents server extensions absent from the portable 1.0 schema.
        schema["$defs"]["streamableHttpServer"]["properties"]["extensions"] = {
            "type": "object", "required": ["com.openai"],
            "properties": {"com.openai": {"type": "object", "required": ["auth"],
                "properties": {"auth": {"const": {
                    "type": "oauth", "client": {"mode": "dcr"},
                    "baseScopes": ["mcp:read", "mcp:write"],
                }}}, "additionalProperties": False}}, "additionalProperties": False,
        }
        Draft202012Validator(schema).validate(mc)
        require(set(mc["mcpServers"]) == {"attention"}, "Unexpected MCP server")
        server = mc["mcpServers"]["attention"]
        require(server.get("url") == "https://api.attention.tech/mcp", "Expected production MCP endpoint")
        require(server.get("type") == "streamable-http" and "extensions" in server,
                "Explicit OpenAI OAuth configuration is required")
        require(not server.get("headers"), "Public upload must not contain credential headers")
        legacy = json.loads(claude.read(".mcp.json"))
        require(legacy == {"mcpServers": {"attention": {
            "type": "http", "url": server["url"],
        }}}, "Claude MCP configuration changed")
        ext = om["extensions"]["com.openai"]
        require(om.get("apps") is None and ext.get("apps") is None,
                "Author-supplied upload must not contain app bindings")
        interface = ext["interface"]
        for field, limit in {"displayName": 30, "shortDescription": 30,
                             "longDescription": 4000, "developerName": 80}.items():
            value = interface.get(field, "")
            require(isinstance(value, str) and value.strip() and len(value) <= limit,
                    f"Invalid listing field: {field}")
        require(interface["category"] == "Productivity", "Unexpected package category")
        for field in ("logo", "composerIcon"):
            require(interface.get(field) == "./assets/attention-icon.png", f"Invalid asset: {field}")
        icon = openai.read("assets/attention-icon.png")
        require(icon[:8] == b"\x89PNG\r\n\x1a\n" and len(icon) <= 5 * 1024 * 1024,
                "Expected a PNG icon under 5 MiB")
        width, height = struct.unpack(">II", icon[16:24])
        require(width == height and width >= 256, "Listing icon must be square and at least 256 px")
        gaps = []
        for field in ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"):
            value = interface.get(field)
            if not value:
                gaps.append(field)
            else:
                url = urlsplit(value)
                require(url.scheme == "https" and url.hostname and not url.username
                        and not url.password and len(value) <= 1024, f"Invalid listing URL: {field}")
        review = ext.get("review", {})
        if not review.get("demo_recording_url"):
            gaps.append("demo_recording_url")
        cases = review.get("test_cases", {})
        if len(cases.get("positive", [])) != 5 or len(cases.get("negative", [])) != 3:
            gaps.append("five positive and three negative reviewer cases")
        if not ext.get("publication", {}).get("release_notes"):
            gaps.append("release_notes")
        with tempfile.TemporaryDirectory() as directory:
            claude.extractall(directory)
            subprocess.run(["claude", "plugin", "validate", directory, "--strict", "--json"],
                           check=True, capture_output=True, text=True)
        require(not submission or not gaps, "Missing submission inputs: " + ", ".join(gaps))
        return {"version": om["version"], "package_validation": "passed",
                "submission_ready": False, "missing_package_inputs": gaps,
                "portal_requirements": ["verified publisher and country choice", "reviewer credentials",
                    "current tool scan and domain verification", "executed reviewer cases and attestations"],
                "archives": [{"name": Path(p).name,
                    "sha256": hashlib.sha256(Path(p).read_bytes()).hexdigest()}
                    for p in (claude_path, openai_path)]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("claude", type=Path)
    parser.add_argument("openai", type=Path)
    parser.add_argument("--submission", action="store_true", help="Fail for missing publication inputs")
    args = parser.parse_args()
    print(json.dumps(validate(args.claude, args.openai, args.submission), indent=2))
