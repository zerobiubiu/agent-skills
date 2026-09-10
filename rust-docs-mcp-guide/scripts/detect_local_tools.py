#!/usr/bin/env python3
"""只读探测 rust-docs-mcp / Ix 本地 CLI 与常见 Ix Skill 文件。

该脚本不检测 Agent 已连接的 MCP tools，因为 MCP capability 属于宿主会话信息，
应由 Agent 从自身 tool inventory 判断。

不安装依赖、不修改配置、不启动 MCP server、不启动 Ix backend。
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


def run_probe(argv: list[str], timeout: float = 4.0) -> dict:
    try:
        proc = subprocess.run(
            argv,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": proc.stdout.strip()[:2000],
            "stderr": proc.stderr.strip()[:2000],
        }
    except Exception as exc:  # noqa: BLE001 - probe must always return structured output
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def existing_ix_skill_paths() -> list[str]:
    home = Path.home()
    cwd = Path.cwd()
    candidates = [
        home / ".agents" / "skills" / "ix" / "SKILL.md",
        home / ".claude" / "skills" / "ix" / "SKILL.md",
        cwd / ".agents" / "skills" / "ix" / "SKILL.md",
        cwd / ".claude" / "skills" / "ix" / "SKILL.md",
    ]
    return [str(path) for path in candidates if path.is_file()]


def main() -> None:
    rust_docs = shutil.which("rust-docs-mcp")
    ix = shutil.which("ix")

    result = {
        "rust_docs_mcp": {
            "cli_available": bool(rust_docs),
            "path": rust_docs,
            "probe": run_probe([rust_docs, "--help"]) if rust_docs else None,
        },
        "ix": {
            "cli_available": bool(ix),
            "path": ix,
            "probe": run_probe([ix, "--help"]) if ix else None,
            "mcp_subcommand_probe": run_probe([ix, "mcp", "--help"]) if ix else None,
            "skill_files": existing_ix_skill_paths(),
            "skill_file_detected": bool(existing_ix_skill_paths()),
        },
        "notes": [
            "MCP connections cannot be reliably detected from this local script.",
            "The Agent must inspect its own tool inventory for rust-docs and Ix MCP capabilities.",
            "Ix Skill presence does not prove the Ix CLI/backend is usable.",
        ],
        "environment": {
            "cwd": os.getcwd(),
            "home": str(Path.home()),
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
