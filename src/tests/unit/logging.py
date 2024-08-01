import unittest
import atexit

from ...loe_simp_app_fw.logger.middleware import Middleware
from ...loe_simp_app_fw import Logger
from ...loe_simp_app_fw.exit import Register

# Unregister exit function because teardown does the same
atexit.unregister(Register.write_log_buffer)

class TestLogger(unittest.TestCase):
    def setUp(self) -> None:
        Logger.bootstrap(
            "./log",
        )
    
    def tearDown(self) -> None:
        Logger._middleware = Middleware()
        Logger._isInit = False
        return

    def test_logging(self) -> None:
        self.assertIsNone(Logger.debug("This is a debug message"))
        self.assertIsNone(Logger.info("This is a info message"))
        self.assertIsNone(Logger.warning("This is a warning message"))
        self.assertIsNone(Logger.error("This is a error message"))
    
    @unittest.expectedFailure
    def test_bootstrap_duplication(self) -> None:
        self.assertIsNone(Logger.bootstrap(
            "./log"
        ))

    @unittest.expectedFailure
    def test_switch_duplication(self) -> None:
        self.assertIsNone(Logger._middleware._switch_none_to_backend_s())
        
