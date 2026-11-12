"""Build Claude and OpenAI archives from the shared Attention sources."""

import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

OPENAI = Path(__file__).resolve().parent
ROOT = OPENAI.parent


def build(output_dir: Path = OPENAI / "dist") -> tuple[Path, Path]:
    manifest = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    manifest.update(json.loads((OPENAI / "manifest-overlay.json").read_text(encoding="utf-8")))
    manifest["$schema"] = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"

    mcp = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))
    mcp["$schema"] = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
    server = mcp["mcpServers"]["attention"]
    server["type"] = "streamable-http"
    server["extensions"] = {"com.openai": {"auth": {
        "type": "oauth", "client": {"mode": "dcr"},
        "baseScopes": ["mcp:read", "mcp:write"],
    }}}

    shared = {"LICENSE": (ROOT / "LICENSE").read_bytes()}
    for path in sorted((ROOT / "skills").rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Cannot package symlink: {path}")
        if path.is_file():
            shared[path.relative_to(ROOT).as_posix()] = path.read_bytes()
    claude = dict(shared)
    for name in (".claude-plugin/plugin.json", ".mcp.json", "README.md"):
        claude[name] = (ROOT / name).read_bytes()
    openai = dict(shared)
    openai["plugin.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    openai["mcp.json"] = (json.dumps(mcp, indent=2) + "\n").encode()
    for path in sorted((OPENAI / "assets").rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Cannot package symlink: {path}")
        if path.is_file():
            openai[path.relative_to(OPENAI).as_posix()] = path.read_bytes()

    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for flavor, files in (("claude", claude), ("openai", openai)):
        output = output_dir / f"attention-{flavor}-{manifest['version']}.zip"
        with ZipFile(output, "w") as archive:
            for name, content in sorted(files.items()):
                info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                info.compress_type = ZIP_DEFLATED
                archive.writestr(info, content)
        outputs.append(output)
    return tuple(outputs)


if __name__ == "__main__":
    for output in build():
        print(output)
