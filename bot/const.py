"""Consts."""
VERSION = "0.1.0"
APP_ID = 38284
REPOSITORY = "custom-components/hacs"
NAME = "hacs-bot"

GREETING_PR = """Hi, @{} 👋
Automatic tasks are now running some initial checks before this can be merged.
When those are done, someone will manually ensure that that it's OK. 💃

While you wait, you can have a look at [this cute kitten 😺](https://www.youtube.com/watch?v=0Bmhjf0rKe8)
"""

CLOSED_ISSUE = """
Hi, @{}

This issue is closed, closed issues are ignored.
If you have issues similar to this, please open a seperate issue.

https://github.com/custom-components/hacs/issues/new/choose

And remember to fill out the entire issue template :)
"""

FOOTER = "\n\n\n_This message was automatically generated 🚀_"


LABEL_NEW_REPO = "New default repository"
LABEL_DOCUMENTATION = "Documentation"
LABEL_BACKEND = "Backend"
LABEL_FRONTEND = "Frontend"


MULTIPLE_FILES_CHANGED = """
This PR changed more then 1 file, because of that automagicall checks can not be exceuted.

Someone will manually ensure that that it's OK. 💃+
"""

REPO_NOT_ACCEPTED_TITLE = "❗️ Hello there, this will not work 😖"
REPO_NOT_ACCEPTED_BODY = """Hi, @{} 👋
This bot can **only** be used with the [HACS](https://github.com/custom-components/hacs) repository.

[There is some good news, the code for this bot can be found here, if you want to run your own version of this.](https://github.com/ludeeus/hacs-bot)
_No docs will be provided, it fluxes too much for that too make sense._

Feel free to close this issue, but make sure you remove this bot from your repository.

![sunset](https://upload.wikimedia.org/wikipedia/commons/thumb/5/58/Sunset_2007-1.jpg/1280px-Sunset_2007-1.jpg)
"""
