import sys, os
# Ensure project root is on path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from main import robot_agent, FormDataRobotAPIClient  # noqa: F401
