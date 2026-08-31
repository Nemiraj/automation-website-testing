import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

try:
    from backend.models import TestRun
except ImportError:
    try:
        from models import TestRun
    except ImportError:
        from ..models import TestRun


class JsonReportGenerator:
    @staticmethod
    def generate(test_run: TestRun) -> str:
        return test_run.model_dump_json(indent=2)
