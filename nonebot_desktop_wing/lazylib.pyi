from typing import List
from nb_cli import handlers as _handlers
from nb_cli import config as _config
from nb_cli.config import Driver, Plugin, Adapter


class _nb_cli:
    handlers = _handlers
    config = _config


nb_cli: _nb_cli

RawInfo = dict[
    {
        "module_name": str,
        "project_link": str,
        "name": str,
        "desc": str,
        "author": str,
        "homepage": str,
        "tags": List[dict[{"label": str, "color": str}]],
        "is_official": bool
    }
]


class _meta:
    drivers: List[Driver]
    adapters: List[Adapter]
    plugins: List[Plugin]
    raw_drivers: List[RawInfo]
    raw_adapters: List[RawInfo]
    raw_plugins: List[RawInfo]


meta: _meta