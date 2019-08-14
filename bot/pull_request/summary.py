"""Create a summary."""

def summary(self, repo, repochecks):
    # Get the current comments
    current = []

    message = f"## Checks for `{repo}`\n\n[Repository link](https://github.com/{repo})\n\nStatus | Check\n-- | --\n"
    if message in current:
        # If comment exist update.
        pass 
    else:
        # If not create.
        pass


    message += "### Core checks\n\nStatus | Check\n-- | --\n"

    for check in self.const.CORE_CHECKS:
        status = "✔️" if repochecks[check]["status"] else "❌"
        message += f"{status} | {repochecks[check]['description'].capitalize()}"


    message += f"### Checks for {self.category}\n\nStatus | Check\n-- | --\n"
    for check in repochecks:
        if check in self.const.CORE_CHECKS:
            continue
        status = "✔️" if repochecks[check]["status"] else "❌"
        message += f"{status} | {repochecks[check]['description'].capitalize()}"
