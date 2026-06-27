"""Config + integration toggles. Everything off => fully offline, deterministic demo."""
import os
from pathlib import Path


def _load_dotenv():
    """Minimal .env loader (no dependency). Does not override existing env vars."""
    path = Path(__file__).resolve().parent.parent / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_dotenv()

USE_REAL_GEMINI = os.getenv("USE_REAL_GEMINI", "0") == "1"
USE_REAL_TRENDS = os.getenv("LEDGERSCOUT_TRENDS_LIVE", "0") == "1"
USE_REAL_RESALE = os.getenv("LEDGERSCOUT_RESALE_LIVE", "0") == "1"
USE_REAL_EUROSTAT = os.getenv("LEDGERSCOUT_EUROSTAT_LIVE", "0") == "1"
USE_REAL_HF = os.getenv("LEDGERSCOUT_HF_LIVE", "0") == "1"

GEMINI_TEXT_MODEL = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash")

# Stripe payments — agents pay for premium datasets with real (test-mode) charges.
# Off by default: a local simulator mirrors the same budget/approval policy so the
# demo is deterministic with no network.
USE_REAL_STRIPE = os.getenv("LEDGERSCOUT_STRIPE_LIVE", "0") == "1"
STRIPE_CURRENCY = os.getenv("LEDGERSCOUT_CURRENCY", "eur")
