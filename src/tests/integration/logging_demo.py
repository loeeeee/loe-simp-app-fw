from ...loe_simp_app_fw import Logger
import time

def logging_no_error() -> None:
    Logger.debug("This is a debug message")
    Logger.info("This is a info message")
    Logger.warning("This is a warning message")

def main() -> None:
    logging_no_error()
    print("BOOTSTRAP")
    Logger.bootstrap("./log")
    print("Finish Bootstrap")
    for _ in range(200):
        logging_no_error()
    Logger.error("This is a error message")
    time.sleep(3)
    print("Finish logging")
    Logger._debootstrap()
    print("Stopped")

    # -----------------------------------------------------
    logging_no_error()
    print("Force single process logger")
    Logger.bootstrap("./log", isMultiprocessing=False)
    logging_no_error()
    print("Finish logging")

if __name__ == "__main__":
    main()