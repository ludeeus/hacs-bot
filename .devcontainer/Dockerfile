FROM python:3.7

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install black pylint colorlog

WORKDIR /workspaces

# Set the default shell to bash instead of sh
ENV SHELL /bin/bash