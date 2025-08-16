import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional


@dataclass
class JSONLogger:
    log_dir: str
    conversation_id: Optional[str] = None
    log_path: Path = field(init=False)

    def __post_init__(self):
        self.log_dir = Path(self.log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        if not self.conversation_id:
            self.conversation_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_utc")

        self.log_path = self.log_dir / f"voice_orchestrator_{self.conversation_id}.json"

        if not self.log_path.exists():
            envelope = {
                "conversation_id": self.conversation_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "turns": [],
            }
            self._atomic_write(envelope)

    def log_turn(self, turn_id: int, user_text: str, assistant_text: str):
        ts = datetime.now(timezone.utc).isoformat()
        rec = {
            "ts": ts,
            "turn_id": turn_id,
            "user_text": user_text,
            "assistant_text": assistant_text,
        }

        data = self._read_json()
        data["turns"].append(rec)
        self._atomic_write(data)


    def _read_json(self) -> dict:
        with open(self.log_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _atomic_write(self, obj: dict):
        with NamedTemporaryFile("w", delete=False, dir=self.log_dir, encoding="utf-8") as tf:
            json.dump(obj, tf, ensure_ascii=False, indent=2)
            temp_name = tf.name
        Path(temp_name).replace(self.log_path)
