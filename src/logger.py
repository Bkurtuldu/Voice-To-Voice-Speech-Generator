import json
from datetime import datetime, timezone
from pathlib import Path


class JSONLogger:
    def __init__(self, log_dir: str):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        date_tag = datetime.now(timezone.utc).strftime("%Y%m%d")
        self.log_path = self.log_dir / f"voice_orchestrator_{date_tag}.json"

    def log_turn(self, turn_id: int, user_text: str, assistant_text: str):
        ts = datetime.now(timezone.utc).isoformat()
        rec = {
            "ts": ts,
            "turn_id": turn_id,
            "user_text": user_text,
            "assistant_text": assistant_text,
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")