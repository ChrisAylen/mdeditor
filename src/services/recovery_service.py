import json
import os
import sys
import uuid

from datetime import datetime


class RecoveryService:
    RECOVERY_DIR_NAME = "recovery"

    @staticmethod
    def _get_recovery_dir() -> str:
        if sys.platform == "win32":
            base = os.environ.get(
                "LOCALAPPDATA",
                os.path.join(os.path.expanduser("~"), "AppData", "Local"),
            )
        elif sys.platform == "darwin":
            base = os.path.join(
                os.path.expanduser("~"), "Library", "Application Support"
            )
        else:
            base = os.environ.get(
                "XDG_DATA_HOME",
                os.path.join(os.path.expanduser("~"), ".local", "share"),
            )
        return os.path.join(base, "mdeditor", RecoveryService.RECOVERY_DIR_NAME)

    @staticmethod
    def _ensure_recovery_dir() -> str:
        d = RecoveryService._get_recovery_dir()
        os.makedirs(d, exist_ok=True)
        return d

    @staticmethod
    def _doc_path(doc_id: str) -> str:
        return os.path.join(
            RecoveryService._get_recovery_dir(), f"{doc_id}.recovery.md"
        )

    @staticmethod
    def _meta_path(doc_id: str) -> str:
        return os.path.join(
            RecoveryService._get_recovery_dir(), f"{doc_id}.meta.json"
        )

    @staticmethod
    def save_recovery(content: str, original_path: str | None, doc_id: str) -> bool:
        try:
            d = RecoveryService._ensure_recovery_dir()
            doc = RecoveryService._doc_path(doc_id)
            meta = RecoveryService._meta_path(doc_id)
            with open(doc, "w", encoding="utf-8") as f:
                f.write(content)
            metadata = {
                "doc_id": doc_id,
                "original_path": original_path,
                "timestamp": datetime.utcnow().isoformat(),
            }
            with open(meta, "w", encoding="utf-8") as f:
                json.dump(metadata, f)
            return True
        except Exception:
            return False

    @staticmethod
    def load_recovery(doc_id: str) -> str | None:
        try:
            doc = RecoveryService._doc_path(doc_id)
            with open(doc, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return None
        except Exception:
            return None

    @staticmethod
    def load_metadata(doc_id: str) -> dict | None:
        try:
            meta = RecoveryService._meta_path(doc_id)
            with open(meta, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    @staticmethod
    def list_recoveries() -> list[dict]:
        d = RecoveryService._get_recovery_dir()
        if not os.path.isdir(d):
            return []
        recoveries = []
        seen_ids = set()
        for name in os.listdir(d):
            if name.endswith(".meta.json"):
                doc_id = name[: -len(".meta.json")]
                meta = RecoveryService.load_metadata(doc_id)
                if meta:
                    recoveries.append(meta)
                    seen_ids.add(doc_id)
        for name in os.listdir(d):
            if name.endswith(".recovery.md"):
                doc_id = name[: -len(".recovery.md")]
                if doc_id not in seen_ids:
                    try:
                        mtime = os.path.getmtime(
                            os.path.join(d, name)
                        )
                        recoveries.append(
                            {
                                "doc_id": doc_id,
                                "original_path": None,
                                "timestamp": datetime.utcfromtimestamp(
                                    mtime
                                ).isoformat(),
                            }
                        )
                        seen_ids.add(doc_id)
                    except OSError:
                        pass
        return recoveries

    @staticmethod
    def has_recoveries() -> bool:
        return len(RecoveryService.list_recoveries()) > 0

    @staticmethod
    def clear_recovery(doc_id: str) -> bool:
        try:
            doc = RecoveryService._doc_path(doc_id)
            meta = RecoveryService._meta_path(doc_id)
            for p in [doc, meta]:
                if os.path.exists(p):
                    os.remove(p)
            return True
        except Exception:
            return False

    @staticmethod
    def clear_all_recoveries() -> bool:
        try:
            d = RecoveryService._get_recovery_dir()
            if os.path.isdir(d):
                for name in os.listdir(d):
                    os.remove(os.path.join(d, name))
            return True
        except Exception:
            return False
