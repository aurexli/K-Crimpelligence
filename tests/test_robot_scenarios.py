import pytest

from ..main import robot_agent, FormDataRobotAPIClient


# Helper to run the agent synchronously
def run_prompt(prompt: str):
    client = FormDataRobotAPIClient()
    result = robot_agent.run_sync(prompt, deps=client)
    return result.output.actions

@pytest.mark.parametrize(
    "prompt,expected",
    [
        ("Drive 1 meter forward", [{"command": "drive", "distance": 1.0, "direction": "forward"}]),
        ("Move backward 0.5 meters and then stop", [
            {"command": "drive", "distance": 0.5, "direction": "backward"},
            {"command": "stop"},
        ]),
        ("Turn left", [{"command": "turn_left", "degrees": 90}]),
        ("Turn right", [{"command": "turn_right", "degrees": 90}]),
        ("Follow the line on the floor", [{"command": "follow_line"}]),
        ("Spin in place for three seconds", [{"command": "spin", "duration": 3.0}]),
        ("Drive two meters forward then turn left", [
            {"command": "drive", "distance": 2.0, "direction": "forward"},
            {"command": "turn_left", "degrees": 90},
        ]),
        ("Go forward 1.2 meters, turn right, and finally stop", [
            {"command": "drive", "distance": 1.2, "direction": "forward"},
            {"command": "turn_right", "degrees": 90},
            {"command": "stop"},
        ]),
        ("Drive 0.8 meters forward, spin for 2 seconds, then follow line", [
            {"command": "drive", "distance": 0.8, "direction": "forward"},
            {"command": "spin", "duration": 2.0},
            {"command": "follow_line"},
        ]),
        ("Drive 1 meter forward, turn left, drive 0.5 meters backward, spin 1 second, then stop", [
            {"command": "drive", "distance": 1.0, "direction": "forward"},
            {"command": "turn_left", "degrees": 90},
            {"command": "drive", "distance": 0.5, "direction": "backward"},
            {"command": "spin", "duration": 1.0},
            {"command": "stop"},
        ]),
    ],
)
def test_robot_prompts(prompt, expected):
    actions = run_prompt(prompt)
    plain = [a.dict() for a in actions]
    assert plain == expected
