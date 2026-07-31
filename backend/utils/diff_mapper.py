import re
from typing import List


class DiffMapper:
    """
    Maps AI line numbers to valid GitHub diff lines.
    """

    @staticmethod
    def extract_changed_lines(patch: str) -> List[int]:
        """
        Extract all changed line numbers from a unified git diff.
        """

        changed_lines = []

        current_line = 0

        for line in patch.splitlines():

            if line.startswith("@@"):

                match = re.search(
                    r"\+(\d+)",
                    line,
                )

                if match:
                    current_line = int(
                        match.group(1)
                    )

                continue

            if line.startswith("+") and not line.startswith("+++"):
                changed_lines.append(current_line)
                current_line += 1

            elif line.startswith("-"):
                continue

            else:
                current_line += 1

        return changed_lines


diff_mapper = DiffMapper()
# Phase 10 testing