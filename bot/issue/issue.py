"""Handle issues."""
async def handle_issue(self):
    if self.action == "opened":
        known, description = issue_is_known(self.event_data)
        if known:
            self.issue_update.state = "closed"
            self.issue_comment.message = description
            await self.issue_comment.create()
            return

    if self.action == "created":
        if (
            self.event_data.get("comment") is not None
            and self.event_data["issue"].get("pull_request") is None
        ):
            if self.event_data["issue"]["state"] == "closed":
                if (
                    self.event_data["issue"]["closed_at"]
                    != self.event_data["comment"]["created_at"]
                ):
                    print("Someone commented on a closed issue!")
                    self.issue_update.state = "closed"
                    self.issue_comment.message = self.const.CLOSED_ISSUE.format(self.submitter)
                    await self.issue_comment.create()
                    return

def issue_is_known(event_data):
    from known_issues import KNOWN_ISSUES

    for known_issue in KNOWN_ISSUES:
        all_checks_is_present = True
        for check in known_issue["check"]:
            if not all_checks_is_present:
                continue
            if check not in event_data["issue"]["body"]:
                all_checks_is_present = False
        if all_checks_is_present:
            return True, known_issue["description"]
    return False, None
