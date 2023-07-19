from functools import lru_cache
from typing import Any, Dict, List, Literal


@lru_cache
def load_module_data_raw(
    module_name: Literal["adapters", "plugins", "drivers"]
) -> List[Dict[str, Any]]:
    """Get raw module data."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import httpx
    exceptions: List[Exception] = []
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