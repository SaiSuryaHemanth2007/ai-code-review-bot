from collections import defaultdict
from copy import deepcopy


class DuplicateDetector:

    @staticmethod
    def group_issues(issues):

        grouped = defaultdict(list)

        for issue in issues:

            key = (
    issue.get("file", ""),
    issue.get("severity", "").upper(),
    issue.get("comment", "").strip().lower(),
    issue.get("suggestion", "").strip().lower(),
)

            grouped[key].append(issue)

        unique_issues = []

        for duplicates in grouped.values():

            first = deepcopy(duplicates[0])

            first["occurrences"] = len(duplicates)

            first["files"] = sorted(
                list(
                    {
                        issue["file"]
                        for issue in duplicates
                    }
                )
            )

            unique_issues.append(first)

        return unique_issues