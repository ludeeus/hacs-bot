"""Checks for new repos."""


async def new_repo_common(repository, repochecks, files):
    if files[0] == "blacklist":
        return repochecks
    rootcontent = await repository.get_contents("")
    readme_files = ["readme", "readme.md"]
    info_files = ["info", "info.md"]

    repochecks["description"] = {
        "state": repository.description != "",
        "description": "Repository have description",
        "url": None,
    }

    repochecks["manifest"] = {
        "state": False,
        "description": "Repository have a hacs.json file",
        "url": None,  # This needs documentation
    }

    repochecks["readme"] = {
        "state": False,
        "description": "Repository have a readme file",
        "url": None,
    }

    repochecks["info"] = {
        "state": False,
        "description": "Repository have a info file",
        "url": "https://custom-components.github.io/hacs/developer/general/#enhance-the-experience",
    }

    for filename in rootcontent:
        if filename.name == "hacs.json":
            repochecks["manifest"]["state"] = True
            repochecks["manifest"]["url"] = filename.attributes["html_url"]
        if filename.name.lower() in readme_files:
            repochecks["readme"]["state"] = True
            repochecks["readme"]["url"] = filename.attributes["html_url"]
        if filename.name.lower() in info_files:
            repochecks["info"]["state"] = True
            repochecks["info"]["url"] = filename.attributes["html_url"]

    category = files[0]
    if category == "appdaemon":
        print(f"Running tests for appdaemon")

    elif category == "integration":
        print(f"Running tests for integration")

    elif category == "plugin":
        print(f"Running tests for plugin")

    elif category == "python_script":
        print(f"Running tests for python_script")

    elif category == "theme":
        print(f"Running tests for theme")

    return repochecks
