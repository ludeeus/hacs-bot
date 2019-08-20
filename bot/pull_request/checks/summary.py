"""Create a summary."""
# pylint: disable=missing-docstring,line-too-long,broad-except


async def summary(self, repository, repochecks, failed):
    # Get the current comments
    endpoint = f"https://api.github.com/repos/{self.event_data['repository']['full_name']}/pulls/{self.issue_number}/reviews"
    current = await self.session.get(endpoint, headers={"Authorization": f"token {self.token}"})

    for review in current:
        endpoint = f"https://api.github.com/repos/{self.event_data['repository']['full_name']}/pulls/{self.issue_number}/reviews/{review['id']}"
        current = await self.session.delete(endpoint, headers={"Authorization": f"token {self.token}"})

    message = f"## Summary of checks for `{repository.full_name}`\n\n"
    message += f"[Repository link](https://github.com/{repository.full_name})\n"
    message += "Checks was run against "
    message += f"[{repository.attributes['ref'].replace('tags/', '')}]"
    message += f"(https://github.com/{repository.full_name}/tree/{repository.attributes['ref'].replace('tags/', '')})\n\n"

    message += "### Core checks\n\nStatus | Check\n-- | --\n"

    category_checks = {}

    for check in repochecks:
        if check in self.const.CORE_CHECKS:
            status = "✔️" if repochecks[check]["state"] else "❌"
            message += f"{status} | {repochecks[check]['description'].capitalize()}\n"
        else:
            category_checks[check] = repochecks[check]

    if category_checks:
        message += f"### {self.category.title()} checks\n\nStatus | Check\n-- | --\n"
        for check in category_checks:
            status = "✔️" if category_checks[check]["state"] else "❌"
            message += f"{status} | {category_checks[check]['description'].capitalize()}\n"

    print("Adding review.")
    endpoint = f"https://api.github.com/repos/{self.event_data['repository']['full_name']}/pulls/{self.issue_number}/reviews"
    data = {
        "commit_id": self.event_data["pull_request"]["head"]["sha"],
        "event": "APPROVE",
        "body": message
    }
    if failed:
        data["event"] = "REQUEST_CHANGES"

        if self.const.LABEL_MANUAL_REVIEW not in self.issue_update.labels:
            self.issue_update.labels.append(self.const.LABEL_MANUAL_REVIEW)

    await self.session.post(
        endpoint,
        json=data,
        headers={
            "Accept": "application/vnd.github.v3.raw+json",
            "Authorization": f"token {self.token}",
        },
    )