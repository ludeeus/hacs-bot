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
            try:
                manifestcontent = await repository.get_contents("hacs.json", repository.attributes['ref'])
                manifestcontent = json.loads(manifestcontent.content)
            except Exception:
                pass
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
        from pull_request.checks.new_repo_appdaemon import new_repo_appdaemon
        repochecks = await new_repo_appdaemon(repository, repochecks)

    elif category == "integration":
        print(f"Running checks for integration")
        from pull_request.checks.new_repo_integration import new_repo_integration
        repochecks = await new_repo_integration(repository, repochecks)

    elif category == "plugin":
        print(f"Running checks for plugin")
        from pull_request.checks.new_repo_plugin import new_repo_plugin
        repochecks = await new_repo_plugin(repository, repochecks)

    elif category == "python_script":
        print(f"Running checks for python_script")
        from pull_request.checks.new_repo_python_script import new_repo_python_script
        repochecks = await new_repo_python_script(repository, repochecks)

    elif category == "theme":
        print(f"Running checks for theme")
        from pull_request.checks.new_repo_theme import new_repo_theme
        repochecks = await new_repo_theme(repository, repochecks)

    return repochecks
