from ...loe_simp_app_fw import CacheMap, Logger, Cached

from random import random

def main() -> None:
    Logger.bootstrap("./log")

    gcm = CacheMap()
    gcm.setup(
        cache_folder=".cache",
        time_to_live=7,
    )
    cache = Cached(
        identifier="12345",
        content=random_bs(),
        file_extension="txt"
    )
    gcm.append(cache)
    Logger.info("Finish saving")
    
def random_bs() -> str:
    return "\n".join(["".join([str(int(random() * 10)) for _ in range(100)]) for k in range(100)])

if __name__ == "__main__":
    main()