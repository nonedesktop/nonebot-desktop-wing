from functools import cache
from typing import Any, Literal

from nonebot_desktop_wing.models import NoneBotCommonInfo, NoneBotPluginInfo

drivers: list[NoneBotCommonInfo]
adapters: list[NoneBotCommonInfo]
plugins: list[NoneBotPluginInfo]


@cache
def load_module_data_raw(
    module_name: Literal["adapters", "plugins", "drivers"]
) -> list[dict[str, Any]]:
    """Get raw module data."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import httpx
    exceptions: list[Exception] = []
    urls = [
        f"https://registry.nonebot.dev/{module_name}.json",
        f"https://cdn.jsdelivr.net/gh/nonebot/registry@results/{module_name}.json",
        f"https://cdn.staticaly.com/gh/nonebot/registry@results/{module_name}.json",
        f"https://jsd.cdn.zzko.cn/gh/nonebot/registry@results/{module_name}.json",
        f"https://ghproxy.com/https://raw.githubusercontent.com/nonebot/registry/results/{module_name}.json",
    ]
    with ThreadPoolExecutor(max_workers=5) as executor:
        tasks = [executor.submit(httpx.get, url) for url in urls]

        for future in as_completed(tasks):
            try:
                resp = future.result()
                return resp.json()
            except Exception as e:
                exceptions.append(e)

    raise Exception("Download failed", exceptions)


def init_resources() -> None:
    """Initialize index resources (drivers, adapters, and plugins)."""
    global drivers, adapters, plugins
    drivers = [NoneBotCommonInfo.parse_obj(u) for u in load_module_data_raw("drivers")]
    adapters = [NoneBotCommonInfo.parse_obj(u) for u in load_module_data_raw("adapters")]
    plugins = [NoneBotPluginInfo.parse_obj(u) for u in load_module_data_raw("plugins")]