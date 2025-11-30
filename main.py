"""CLI that interprets natural language commands using Pydantic AI and controls a robot via HTTP endpoints.

Run with:
    python main.py "Drive 2 meters forward then turn left 90 degrees"
"""
from __future__ import annotations

import os
import random
from dataclasses import dataclass
from typing import List

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
import httpx
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext


# Agent configuration:
#   Model: openai:gpt-5.1
#   Dependencies: BaseRobotClient provides HTTP client methods
#   Output: RobotOutput (list of action models)
#   Instructions guide the AI to generate an ordered list of actions.


@dataclass
class BaseRobotClient:
    """Simple HTTP client for the robot server."""
    base_url: str = "http://192.168.179.18:80"

    def get(self, path: str, params: dict) -> dict:
        """Send GET request with query parameters and return first action if present."""
        logger.debug(f"GET {path} params={params}")
        with httpx.Client(base_url=self.base_url) as client:
            resp = client.get(path, params=params)
            logger.debug(f"Response {resp.status_code}: {resp.text[:200]}")
            resp.raise_for_status()
            return params

    def send(self, path: str, payload: dict) -> dict:
        return self.get(path, payload)

@dataclass
class FormDataRobotAPIClient(BaseRobotClient):
    """HTTP client that posts form‑data (key=value) instead of JSON. Server returns only status=200 with no body."""
    base_url: str = "http://192.168.179.18:80"

    def _flatten(self, obj: dict, parent: str = "") -> dict:
        """Flatten nested dicts into a single‑level key=value mapping.
        Nested keys are joined with dots, e.g. {"a": {"b": 1}} → {"a.b": 1}.
        """
        items: dict = {}
        for k, v in obj.items():
            key = f"{parent}.{k}" if parent else k
            if isinstance(v, dict):
                items.update(self._flatten(v, key))
            else:
                items[key] = v
        return items

    def get_with_params(self, path: str, params: dict) -> dict:
        logger.debug(f"GET {path} params={params} (flattened)")
        """Send a GET request with query parameters. Returns empty dict because server has no JSON response."""
        flat_data = self._flatten(params)
        with httpx.Client(base_url=self.base_url) as client:
            logger.debug(f"GET {path} params={flat_data}")
            resp = client.get(path, params=flat_data)
            logger.debug(f"Response {resp.status_code}: {resp.text[:200]}")
            resp.raise_for_status()
        return {}

    def send(self, path: str, payload: dict) -> dict:
        return self.get_with_params(path, payload)


from typing import Literal, Union

class DriveAction(BaseModel):
    command: Literal["drive"]
    distance: float
    direction: Literal["forward", "backward"]

class TurnLeftAction(BaseModel):
    command: Literal["turn_left"]
    degrees: Literal[90]

class TurnRightAction(BaseModel):
    command: Literal["turn_right"]
    degrees: Literal[90]

class PauseAction(BaseModel):
    command: Literal["pause"]
    duration: float

class FollowLineAction(BaseModel):
    command: Literal["follow_line"]

class SpinAction(BaseModel):
    command: Literal["spin"]
    duration: float

class RobotOutput(BaseModel):
    """Structured list of robot actions chosen by the AI.

    The AI must output a list where each item matches one of the defined command schemas.
    """
    actions: List[Union[DriveAction, TurnLeftAction, TurnRightAction, PauseAction, FollowLineAction, SpinAction]]


# Model for stop reason output
class ReasonOutput(BaseModel):
    reason: str


# Define the Pydantic AI Agent that interprets natural language into robot actions
robot_agent = Agent(
    "openai:gpt-5.1",
    deps_type=BaseRobotClient,
    output_type=RobotOutput,
    instructions=(
        "You are a robot controller. Convert natural language instructions into a sequence of robot actions using the provided tools. "
        "Return a list of actions in the order they should be performed."
    ),
)

# Second agent to generate dynamic stop reasons based on weather/news in Garching
reason_agent = Agent(
    "openai:gpt-5.1",
    deps_type=None,
    output_type=ReasonOutput,
    instructions=(
        "You are an assistant providing plausible reasons why a robot cannot perform a given action. "
        "Consider current weather and news in Garching. Produce a concise, single-sentence reason."
    ),
)


@robot_agent.tool
# Tool: drive – creates a drive action (distance, direction)
async def drive(
    ctx: RunContext[BaseRobotClient], distance: float, direction: str
) -> dict:
    """Drive the robot a distance (in meters) forward or backward."""
    # Return structured action for the AI
    return {"command": "drive", "distance": distance, "direction": direction}


@robot_agent.tool
# Tool: turn_left – creates a left turn action (degrees)
async def turn_left(
    ctx: RunContext[BaseRobotClient], degrees: int
) -> dict:
    """Turn the robot left by the given number of degrees."""
    return {"command": "turn_left", "degrees": degrees}


@robot_agent.tool
# Tool: turn_right – creates a right turn action (degrees)
async def turn_right(
    ctx: RunContext[BaseRobotClient], degrees: int
) -> dict:
    """Turn the robot right by the given number of degrees."""
    return {"command": "turn_right", "degrees": degrees}


@robot_agent.tool
# Tool: pause – creates a pause action to stop all motion
async def pause(
    ctx: RunContext[BaseRobotClient], duration: float = 0.0
) -> dict:
    """Pause robot motion for a given duration (seconds)."""
    return {"command": "pause", "duration": duration}


@robot_agent.tool
# Tool: follow_line – creates an action to follow a line
async def follow_line(
    ctx: RunContext[BaseRobotClient]
) -> dict:
    """Make the robot follow a line on the ground."""
    return {"command": "follow_line"}

@robot_agent.tool
# Tool: spin – creates a spin action (duration in seconds)
async def spin(
    ctx: RunContext[BaseRobotClient], duration: float
) -> dict:
    """Spin the robot in place by turning wheels opposite directions for a given duration (seconds)."""
    return {"command": "spin", "duration": duration}


def _execute_action(client: BaseRobotClient, act) -> dict:
    """Execute a single RobotOutput action via the HTTP client using a command map."""
    command_map = {
        "drive": lambda: client.get("/drive", {"direction": act.direction, "duration": int(act.distance * 1000)}),
        "turn_left": lambda: client.get("/turn", {"direction": "left", "degree": act.degrees}),
        "turn_right": lambda: client.get("/turn", {"direction": "right", "degree": act.degrees}),
        "pause": lambda: client.get("/pause", {"duration": int(act.duration * 1000)}),
        "follow_line": lambda: client.get("/follow_line", {}),
        "spin": lambda: client.get("/spin", {"duration": int(act.duration * 1000)}),
    }
    return command_map.get(act.command, lambda: {})()



def fetch_dynamic_reason(act) -> str:
    """Use the reason_agent to generate a dynamic stop reason for the given action."""
    try:
        # Prompt includes the action command for context
        prompt = f"Provide a reason why the robot cannot execute the '{act.command}' action right now in Garching."
        result = reason_agent.run_sync(prompt)
        # The agent returns ReasonOutput
        return result.output.reason
    except Exception:
        # Fallback to static reasons if agent fails
        return random.choice([
            "Robot sensors are offline due to a sudden rainstorm.",
            "The robot's battery is critically low and refuses to move.",
            "Visibility is poor; the robot cannot see its path.",
            "Mechanical failure: one wheel is stuck.",
            "External interference: a nearby magnetic field disrupts navigation.",
            "A sudden parade in Garching blocks the robot's path.",
            "The robot got distracted by the scent of fresh pretzels in Garching.",
            "Garching's foggy morning makes navigation impossible."
        ])

def get_stop_reason(act) -> str:
    """Select a reason why the robot cannot execute the action, possibly using dynamic agent."""
    # 50% chance to use dynamic reason when fun features are on
    if random.choice([True, False]):
        return fetch_dynamic_reason(act)
    # Otherwise static random reason
    return random.choice([
        "Robot sensors are offline due to a sudden rainstorm.",
        "The robot's battery is critically low and refuses to move.",
        "Visibility is poor; the robot cannot see its path.",
        "Mechanical failure: one wheel is stuck.",
        "External interference: a nearby magnetic field disrupts navigation.",
        "A sudden parade in Garching blocks the robot's path.",
        "The robot got distracted by the scent of fresh pretzels in Garching.",
        "Garching's foggy morning makes navigation impossible."
    ])

# Feature flag for fun features (set env FUN_FEATURES=1 to enable)
FUN_FEATURES = os.getenv("FUN_FEATURES", "0") == "1"

def main() -> None:
    # client = RobotAPIClient()
    client = FormDataRobotAPIClient()
    print("Enter robot commands (type 'exit' or empty line to quit):")
    while True:
        try:
            instruction = input("> ").strip()
        except EOFError:
            break
        if not instruction or instruction.lower() == "exit":
            break
        result = robot_agent.run_sync(instruction, deps=client)
        for act in result.output.actions:
            if FUN_FEATURES and random.choice([True, False]):
                reason = get_stop_reason(act)
                print(f"Cannot execute {act.command}: {reason}")
            resp = _execute_action(client, act)
            print(f"Executed {act.command}: {resp}")
        print("AI actions:", result.output.actions)


if __name__ == "__main__":
    main()
