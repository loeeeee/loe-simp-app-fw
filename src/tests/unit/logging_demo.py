from ...loe_simp_app_fw import Logger

def logging() -> None:
    Logger.debug("This is a debug message")
    Logger.info("This is a info message")
    Logger.warning("This is a warning message")
    Logger.error("This is a error message")

def main() -> None:
    logging()
    print("BOOTSTRAP")
    Logger.bootstrap("./log")
    print("Finish Bootstrap")
    logging()
    print("Finish main")

if __name__ == "__main__":
    main()