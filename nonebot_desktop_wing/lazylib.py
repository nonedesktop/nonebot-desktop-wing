import asyncio
from nonebot_desktop_wing.hindsight import BackgroundObject
from nonebot_desktop_wing.molecules import import_with_lock
from nonebot_desktop_wing.resources import load_module_data_raw


class _nb_cli:
    handlers = BackgroundObject(import_with_lock, "nb_cli.handlers", "*")
    config = BackgroundObject(import_with_lock, "nb_cli.config", "*")


nb_cli = _nb_cli()


class _meta:
    drivers = BackgroundObject(asyncio.run, nb_cli.handlers.load_module_data("driver"))
    adapters = BackgroundObject(asyncio.run, nb_cli.handlers.load_module_data("adapter"))
    plugins = BackgroundObject(asyncio.run, nb_cli.handlers.load_module_data("plugin"))
    raw_drivers = BackgroundObject(load_module_data_raw, "drivers")
    raw_adapters = BackgroundObject(load_module_data_raw, "adapters")
    raw_plugins = BackgroundObject(load_module_data_raw, "plugins")


meta = _meta()