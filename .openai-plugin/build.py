"""Package shared Attention files with the OpenAI metadata (Python 3.9+)."""

import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

OPENAI = Path(__file__).resolve().parent
ROOT = OPENAI.parent


def build(output_dir: Path = OPENAI / "dist") -> Path:
    manifest = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    manifest.update(json.loads((OPENAI / "manifest-overlay.json").read_text(encoding="utf-8")))
    manifest["$schema"] = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"

    mcp = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))
    mcp["$schema"] = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
    for server in mcp["mcpServers"].values():
        if server.get("type") == "http":
            server["type"] = "streamable-http"

    files = [(ROOT / "LICENSE", "LICENSE")]
    for directory, base in ((ROOT / "skills", ROOT), (OPENAI / "assets", OPENAI)):
        for path in sorted(directory.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"Cannot package symlink: {path}")
            if path.is_file():
                files.append((path, path.relative_to(base).as_posix()))

    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"attention-openai-{manifest['version']}.zip"
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr("plugin.json", json.dumps(manifest, indent=2) + "\n")
        archive.writestr("mcp.json", json.dumps(mcp, indent=2) + "\n")
        for source, name in files:
            archive.write(source, name)
    return output


if __name__ == "__main__":
    print(build())
