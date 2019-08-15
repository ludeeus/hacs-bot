"""Handle closed issues."""
# pylint: disable=missing-docstring


async def handle_closed_issue(self):
    if self.event_data.get("comment") is not None:
        if self.event_data["issue"].get("pull_request") is None:
            if self.event_data["issue"]["state"] == "closed":
                if (
                    self.event_data["issue"]["closed_at"]
                    != self.event_data["comment"]["created_at"]
                ):
                    print("Someone commented on a closed issue!")
                    self.issue_update.state = "closed"
                    self.issue_comment.message = self.const.CLOSED_ISSUE.format(
                        self.submitter
                    )
                    await self.issue_comment.create()
                    return True
    return False
