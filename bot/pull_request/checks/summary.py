"""Create a summary."""
# pylint: disable=missing-docstring,line-too-long,broad-except


async def summary(self, repo, repochecks):
    # Get the current comments
    current = await self.repository.list_issue_comments(self.issue_number)
    update = False
    comment_id = None

    message = f"## Summary of checks for `{repo}`\n\n"
    for comment in current:
        if message in comment.body:
            update = True
            comment_id = comment.id

    message += f"[Repository link](https://github.com/{repo})\n\n"

    message += "### Core checks\n\nStatus | Check\n-- | --\n"

    for check in self.const.CORE_CHECKS:
        status = "✔️" if repochecks[check]["state"] else "❌"
        message += f"{status} | {repochecks[check]['description'].capitalize()}\n"
        del repochecks[check]

    if repochecks:
        message += f"### Checks for {self.category}\n\nStatus | Check\n-- | --\n"
        for check in repochecks:
            status = "✔️" if repochecks[check]["state"] else "❌"
            message += f"{status} | {repochecks[check]['description'].capitalize()}\n"

    self.issue_comment.message = message
    if update:
        await self.issue_comment.update(comment_id)
    else:
        await self.issue_comment.create()
