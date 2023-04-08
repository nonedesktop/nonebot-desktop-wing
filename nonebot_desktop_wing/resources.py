from functools import cache
from typing import Any, Dict, List, Literal


@cache
def load_module_data_raw(
    module_name: Literal["adapters", "plugins", "drivers"]
) -> List[Dict[str, Any]]:
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import httpx
    exceptions: List[Exception] = []
    urls = [
        f"https://v2.nonebot.dev/{module_name}.json",
        f"https://raw.fastgit.org/nonebot/nonebot2/master/website/static/{module_name}.json",
        f"https://cdn.jsdelivr.net/gh/nonebot/nonebot2/website/static/{module_name}.json",
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