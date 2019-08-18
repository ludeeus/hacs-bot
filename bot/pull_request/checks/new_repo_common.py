"""Checks for new repos."""
import json


async def new_repo_common(repository, repochecks, files):
    if files[0] == "blacklist":
        return repochecks
    rootcontent = await repository.get_contents("", repository.attributes['ref'])
    readme_files = ["readme", "readme.md"]
    info_files = ["info", "info.md"]

    repochecks["description"] = {
        "state": repository.description != "",
        "description": "Repository have description",
        "url": "https://hacs.netlify.com/developer/general/#description",
    }

    repochecks["manifest"] = {
        "state": False,
        "description": "Repository have a hacs.json file",
        "url": "https://hacs.netlify.com/developer/general/#hacsjson",
    }

    repochecks["readme"] = {
        "state": False,
        "description": "Repository have a readme file",
        "url": "https://hacs.netlify.com/developer/general/#readme",
    }

    repochecks["info"] = {
        "state": False,
        "description": "Repository have a info file",
        "url": "https://hacs.netlify.com/developer/general/#infomd",
    }

    manifestcontent = None
    for filename in rootcontent:
        if filename.name == "hacs.json":
            repochecks["manifest"]["state"] = True
            repochecks["manifest"]["url"] = filename.attributes["html_url"]

            manifestcontent = await repository.get_contents("hacs.json", repository.attributes['ref'])
            manifestcontent = json.loads(manifestcontent.content)
        if filename.name.lower() in readme_files:
            repochecks["readme"]["state"] = True
            repochecks["readme"]["url"] = filename.attributes["html_url"]
        if filename.name.lower() in info_files:
            repochecks["info"]["state"] = True
            repochecks["info"]["url"] = filename.attributes["html_url"]

    # TODO: Enabled after 0.14.0 of HACS
    # if manifestcontent is not None:
    #    if manifestcontent.get("render_readme"):
    #        del repochecks["info"]

    if manifestcontent is not None:
        repochecks["hacs.json - name"] = {
            "state": "name" in manifestcontent,
            "description": "The hacs.json file have a name key",
            "url": "https://hacs.netlify.com/developer/general/#hacsjson",
        }

    category = files[0].split("/")[-1]
    if category == "appdaemon":
        print(f"Running checks for appdaemon")

    elif category == "integration":
        print(f"Running checks for integration")
        from pull_request.checks.new_repo_integration import new_repo_integration
        repochecks = await new_repo_integration(repository, repochecks)

    elif category == "plugin":
        print(f"Running checks for plugin")

    elif category == "python_script":
        print(f"Running checks for python_script")

    elif category == "theme":
        print(f"Running checks for theme")

    return repochecks
