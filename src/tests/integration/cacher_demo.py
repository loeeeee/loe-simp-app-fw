from ...loe_simp_app_fw import CacheManager, Logger, Cached

from random import random

def main() -> None:
    Logger.bootstrap("./log", log_level="DEBUG")

    gcm = CacheManager()
    gcm.setup(
        cache_folder=".cache",
        time_to_live=7,
    )
    for _ in range(3):
        new_id = random_bs_small()
        cache = Cached.from_content(
            identifier=new_id,
            content=random_bs(),
            file_extension="txt"
        )
        gcm.append(cache)
    Logger.info("Finish saving")
    
def random_bs() -> str:
    return "\n".join(["".join([str(int(random() * 10)) for _ in range(100)]) for k in range(100)])

def random_bs_small() -> str:
    return "".join([str(int(random()*10)) for _ in range(100)])

if __name__ == "__main__":
    main()