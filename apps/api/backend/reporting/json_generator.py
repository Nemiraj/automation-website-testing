import json
from ..models import TestRun


class JsonReportGenerator:
    @staticmethod
    def generate(test_run: TestRun) -> str:
        return test_run.model_dump_json(indent=2)
