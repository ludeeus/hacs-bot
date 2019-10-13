"""Handle pull requests."""
# pylint: disable=no-name-in-module, missing-docstring
from pull_request.new_repository import new_repository
from pull_request.diff import get_pr_diff_data


async def handle_pull_request(self):
    self.branch = self.event_data["pull_request"]["base"]["ref"]
    if self.action == "opened":
        self.issue_comment.message = self.const.GREETING_PR.format(self.submitter)
        await self.issue_comment.create()

    files, added, removed = await get_pr_diff_data(
        self.session, self.event_data, self.issue_number
    )

    for changed_file in files:
        if changed_file.startswith("/documentation/"):
            if self.const.LABEL_DOCUMENTATION not in self.issue_update.labels:
                self.issue_update.labels.append(self.const.LABEL_DOCUMENTATION)
        if changed_file.startswith("/custom_components/hacs/frontend/") or changed_file.startswith("/frontend/"):
            if self.const.LABEL_FRONTEND not in self.issue_update.labels:
                self.issue_update.labels.append(self.const.LABEL_FRONTEND)
        if changed_file.endswith(".py"):
            if self.const.LABEL_BACKEND not in self.issue_update.labels:
                self.issue_update.labels.append(self.const.LABEL_BACKEND)

    if self.branch == "data":
        await new_repository(self, files, added, removed)
