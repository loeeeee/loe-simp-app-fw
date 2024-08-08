from ...loe_simp_app_fw import Logger
import time

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
    time.sleep(5)
    print("Finish logging")
    Logger._debootstrap()
    print("Stopped")

    # -----------------------------------------------------
    logging()
    print("Force single process logger")
    Logger.bootstrap("./log", isMultiprocessing=False)
    logging()
    print("Finish logging")

if __name__ == "__main__":
    main()