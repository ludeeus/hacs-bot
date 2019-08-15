"""Handle known issues."""
# pylint: disable=missing-docstring
KNOWN_ISSUES = [
    {
        "check": ["Missing migration step for 4"],
        "description": "HACS version 0.13.0+ can **only** migrate from version 0.12.0+.\n\nTo fix this issue you need to first upgrade to version 0.12.0, then upgrade to 0.13.0\n\nOr you can delete all the files containing `hacs` in the `.storage` directory and restart Home Assistant **(NB!: This will delete the status of the repositories you have installed.)**",
    }
]


async def handle_known_issue(self):
    for known_issue in KNOWN_ISSUES:
        all_checks_is_present = True
        for check in known_issue["check"]:
            if not all_checks_is_present:
                continue
            if check not in self.event_data["issue"]["body"]:
                all_checks_is_present = False
        if all_checks_is_present:
            self.issue_update.state = "closed"
            self.issue_comment.message = known_issue["description"]
            await self.issue_comment.create()
            return True
    return False
