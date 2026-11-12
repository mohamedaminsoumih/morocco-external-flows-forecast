"""Project settings: paths and the series we forecast."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# Series name → pattern of the Office des Changes file name.
# Patterns (not exact names) because the number at the end
# changes each time the Office des Changes publishes a new version.
SERIES = {
    "mre_remittances": "Evol_MRE_*",
    "travel_receipts": "Evol_recettes_Voyages_*",
}

REPORTS_DIR = PROJECT_ROOT / "reports"
