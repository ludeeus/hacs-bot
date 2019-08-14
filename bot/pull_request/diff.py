"""Get the PR diff."""

async def get_pr_diff_data(session, event_data, issue_number):
    base = "https://patch-diff.githubusercontent.com/raw"
    repo = event_data['repository']['full_name']

    files = []
    added = []
    removed = []

    diff = await session.get(
        f"{base}/{repo}/pull/{issue_number}.diff"
    )
    diff = await diff.text()

    for line in diff.split("\n"):
        if line.startswith("+++ b"):
            files.append(line.split("+++ b")[1])
        elif line.startswith("-"):
            if '"' in line:
                removed.append(line.split('"')[1])
        elif line.startswith("+"):
            if '"' in line:
                added.append(line.split('"')[1])

    print(f"{files} - {added} - {removed}")

    return files, added, removed
