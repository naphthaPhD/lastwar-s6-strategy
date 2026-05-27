from __future__ import annotations

import argparse
import json
import mimetypes
import subprocess
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse


REPO_ROOT = Path(__file__).resolve().parents[2]
TOOL_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG = TOOL_DIR / "config.google_full_map.json"
DEFAULT_STATE = REPO_ROOT / "sample_output" / "state.json"
DEFAULT_OVERRIDES = REPO_ROOT / "data" / "invasion_strategy_overrides.json"
APP_HTML = TOOL_DIR / "interactive_app.html"
GENERATOR = TOOL_DIR / "invasion_strategy_os.py"

EDITABLE_NODE_FIELDS = {
    "owner",
    "status",
    "memo",
    "importance",
    "type",
    "protect_until",
}


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def normalize_overrides(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {"nodes": {}}
    nodes = raw.get("nodes", raw)
    if not isinstance(nodes, dict):
        nodes = {}

    normalized_nodes: dict[str, dict[str, Any]] = {}
    for node_id, override in nodes.items():
        if not isinstance(node_id, str) or not isinstance(override, dict):
            continue
        cleaned = {
            key: value
            for key, value in override.items()
            if key in EDITABLE_NODE_FIELDS and value is not None
        }
        if cleaned:
            normalized_nodes[node_id] = cleaned
    return {"nodes": normalized_nodes}


def merged_state(state_path: Path, overrides_path: Path) -> dict[str, Any]:
    state = read_json(state_path, {"nodes": [], "connections": []})
    overrides = normalize_overrides(read_json(overrides_path, {"nodes": {}}))
    node_overrides = overrides["nodes"]

    for node in state.get("nodes", []):
        if not isinstance(node, dict):
            continue
        node_id = node.get("id")
        if node_id not in node_overrides:
            continue
        node["original"] = {
            key: node.get(key)
            for key in node_overrides[node_id].keys()
            if key in node
        }
        node.update(node_overrides[node_id])
        node["manual_override"] = True

    state["overrides"] = overrides
    return state


def is_inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


class InteractiveMapHandler(BaseHTTPRequestHandler):
    server_version = "LastWarInteractiveMap/0.1"
    config_path: Path
    state_path: Path
    overrides_path: Path

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"{self.address_string()} - {fmt % args}")

    def send_bytes(self, content: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(content)

    def send_cors_headers(self) -> None:
        origin = self.headers.get("Origin", "")
        if origin.startswith(("http://127.0.0.1:", "http://localhost:")):
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def send_json(self, data: Any, status: int = 200) -> None:
        content = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_bytes(content, "application/json; charset=utf-8", status)

    def send_error_json(self, message: str, status: int = 400, **extra: Any) -> None:
        payload = {"ok": False, "error": message}
        payload.update(extra)
        self.send_json(payload, status)

    def read_request_json(self) -> Any:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length > 2_000_000:
            raise ValueError("Request body is too large")
        raw = self.rfile.read(content_length)
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in {"/", "/interactive.html"}:
            self.serve_file(APP_HTML)
            return
        if path == "/api/state":
            self.send_json(merged_state(self.state_path, self.overrides_path))
            return
        if path == "/api/overrides":
            self.send_json(normalize_overrides(read_json(self.overrides_path, {"nodes": {}})))
            return
        if path.startswith("/sample_output/"):
            self.serve_static(path)
            return
        self.send_error_json("Not found", HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/overrides":
            try:
                overrides = normalize_overrides(self.read_request_json())
            except Exception as exc:
                self.send_error_json(f"Invalid overrides JSON: {exc}")
                return
            write_json(self.overrides_path, overrides)
            self.send_json({"ok": True, "overrides": overrides})
            return
        if path == "/api/refresh":
            self.refresh_from_sheet()
            return
        self.send_error_json("Not found", HTTPStatus.NOT_FOUND)

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_cors_headers()
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def refresh_from_sheet(self) -> None:
        command = [
            sys.executable,
            str(GENERATOR),
            "--config",
            str(self.config_path),
        ]
        try:
            completed = subprocess.run(
                command,
                cwd=REPO_ROOT,
                capture_output=True,
                check=False,
                text=True,
                encoding="utf-8",
                timeout=120,
            )
        except Exception as exc:
            self.send_error_json(f"Refresh failed to start: {exc}", HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        self.send_json(
            {
                "ok": completed.returncode == 0,
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            },
            200 if completed.returncode == 0 else HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    def serve_static(self, request_path: str) -> None:
        relative = unquote(request_path).lstrip("/")
        path = REPO_ROOT / relative
        if not is_inside(path, REPO_ROOT / "sample_output"):
            self.send_error_json("Static path is outside sample_output", HTTPStatus.FORBIDDEN)
            return
        self.serve_file(path)

    def serve_file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self.send_error_json("File not found", HTTPStatus.NOT_FOUND)
            return
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if path.suffix.lower() in {".html", ".css", ".js"}:
            content_type += "; charset=utf-8"
        self.send_bytes(path.read_bytes(), content_type)


def build_handler(config_path: Path, state_path: Path, overrides_path: Path) -> type[InteractiveMapHandler]:
    class Handler(InteractiveMapHandler):
        pass

    Handler.config_path = config_path
    Handler.state_path = state_path
    Handler.overrides_path = overrides_path
    return Handler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve the interactive LastWar map editor.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8010)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--overrides", type=Path, default=DEFAULT_OVERRIDES)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    handler = build_handler(args.config.resolve(), args.state.resolve(), args.overrides.resolve())
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Serving interactive map: http://{args.host}:{args.port}/")
    print(f"State: {args.state}")
    print(f"Overrides: {args.overrides}")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
