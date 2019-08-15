"""Handle issues."""
# pylint: disable=no-name-in-module, broad-except, missing-docstring
from issue.known import handle_known_issue
from issue.closed import handle_closed_issue


async def handle_issue(self):
    if self.action == "opened":
        if await handle_known_issue(self):
            return

    if self.action == "created":
        if await handle_closed_issue(self):
            return

