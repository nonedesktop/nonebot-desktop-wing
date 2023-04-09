# nonebot-desktop-wing

Wings for NoneBot desktop applications.

## Installation

```console
pip install nonebot-desktop-wing
```

## Contents

### Constants

|Name        |Description|
|:-----------|:----------|
|PYPI_MIRRORS|A list of PyPI indices for choosing.|

### Hindsight

|Name            |Description|
|:---------------|:----------|
|BackgroundObject|Run a function in background. Usually for faster loading in GUI.|

### Lazylib

Provide some import and resources with BackgroundObject.

### Molecules

|Name               |Description|
|:------------------|:----------|
|import_with_lock   |Prevent multiple importing the same package at the same time.|
|list_paginate      |Cut a list for paging.|
|exec_new_win       |Execute shell commands in a new window.|
|open_new_win       |Open a new command-line window.|
|system_open        |Use applications in system to open a file or uri.|
|perform_pip_command|Run pip command with specified arguments.|
|perform_pip_install|Run pip install command with specified arguments.|
|rrggbb_bg2fg       |Get foreground color from background color. (#RRGGBB)|

### Project

|Name                       |Description|
|:--------------------------|:----------|
|find_python                |Find a python in a directory.|
|distributions              |Get installed packages in specified dirs.|
|getdist                    |Get installed packages in a project.|
|create                     |Create a new project.|
|get_builtin_plugins        |Get available built-in plugins.|
|find_env_file              |Find dotenv files in a directory.|
|recursive_find_env_config  |Search dotenv files for a configuration in a directory.|
|recursive_update_env_config|Update a configuration in dotenv files in a directory.|
|get_toml_config            |Get toml data manager from a directory.|

### Resources

|Name                |Description|
|:-------------------|:----------|
|load_module_data_raw|Get raw data of NoneBot packages online.|
