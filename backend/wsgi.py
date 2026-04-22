import logging
import os
import subprocess
import sys
from flask import Flask, jsonify, request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _create_fallback_app(boot_error: Exception) -> Flask:
    """Minimal app that keeps deploy webhook available when main app fails to boot."""
    app = Flask(__name__)
    app.logger.setLevel(logging.INFO)
    app.logger.exception("Main app boot failed; fallback deploy app active", exc_info=boot_error)

    deploy_token = os.environ.get("DEV_TOKEN", "")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @app.get("/__boot_error")
    def boot_error_route():
        return jsonify({"error": "main app failed to boot", "detail": str(boot_error)}), 503

    @app.post("/internal/deploy")
    def fallback_deploy_webhook():
        token = request.headers.get("X-Deploy-Token", "")
        if not deploy_token or token != deploy_token:
            return jsonify({"error": "unauthorized"}), 401

        result = subprocess.run(
            ["git", "pull", "origin", "main"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=90,
        )

        if result.returncode == 0:
            # Trigger PythonAnywhere app reload if available.
            reload_file = os.environ.get("PA_WSGI_RELOAD_FILE")
            if reload_file:
                try:
                    with open(reload_file, "a", encoding="utf-8"):
                        os.utime(reload_file, None)
                except OSError:
                    app.logger.warning("Could not touch PA_WSGI_RELOAD_FILE", exc_info=True)

        return jsonify(
            {
                "mode": "fallback",
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        ), (200 if result.returncode == 0 else 500)

    return app


def _create_main_application() -> Flask:
    import api
    import database

    db = database.connect(locally=False)
    return api.create_app(db, is_local=False)


try:
    application = _create_main_application()
except Exception as exc:
    application = _create_fallback_app(exc)
