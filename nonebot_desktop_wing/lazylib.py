import asyncio
from threading import Thread
from nonebot_desktop_wing.hindsight import BackgroundObject
from nonebot_desktop_wing.molecules import import_with_lock
from nonebot_desktop_wing.resources import load_module_data_raw


class _nb_cli:
    __singleton = None

    def __new__(cls):
        if cls.__singleton is None:
            cls.handlers = BackgroundObject(import_with_lock, "nb_cli.handlers", "*")
            cls.config = BackgroundObject(import_with_lock, "nb_cli.config", "*")
            cls.__singleton = object.__new__(cls)
        return cls.__singleton


nb_cli = _nb_cli

Thread(target=_nb_cli).start()


class _meta:
    __singleton = None

    def __new__(cls):
        if cls.__singleton is None:
            # load in __new__ to avoid lagging when getting `nb_cli.handlers`
            cls.drivers = BackgroundObject(asyncio.run, nb_cli().handlers.load_module_data("driver"))
            cls.adapters = BackgroundObject(asyncio.run, nb_cli().handlers.load_module_data("adapter"))
            cls.plugins = BackgroundObject(asyncio.run, nb_cli().handlers.load_module_data("plugin"))
            cls.raw_drivers = BackgroundObject(load_module_data_raw, "drivers")
            cls.raw_adapters = BackgroundObject(load_module_data_raw, "adapters")
            cls.raw_plugins = BackgroundObject(load_module_data_raw, "plugins")
            cls.__singleton = object.__new__(cls)
        return cls.__singleton


meta = _meta

Thread(target=_meta).start()