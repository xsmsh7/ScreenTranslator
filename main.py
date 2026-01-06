import sys
import os

from core.app_controller import AppController

if __name__ == "__main__":
    controller = AppController()
    sys.exit(controller.run())
