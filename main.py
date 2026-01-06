import sys
import os

# Add the current directory to sys.path to ensure relative imports work when running from root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.app_controller import AppController

if __name__ == "__main__":
    controller = AppController()
    sys.exit(controller.run())
