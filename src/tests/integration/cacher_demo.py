from ...loe_simp_app_fw import GlobalCacheManager, Logger

from random import random

def main() -> None:
    Logger.bootstrap("./log")

    gcm = GlobalCacheManager()
    gcm.setup(
        "./.cache",
        days_to_expire=10000,
    )
    gcm.save(random_bs(), "12345", ".txt")
    Logger.info("Finish saving")
    
def random_bs() -> str:
    return "\n".join(["".join([str(int(random() * 10)) for _ in range(100)]) for k in range(100)])

if __name__ == "__main__":
    main()