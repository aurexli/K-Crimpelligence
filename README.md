# k‑crimpelligence

A CLI that interprets natural‑language commands using **Pydantic AI** and sends actions to a robot via HTTP endpoints.

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python main.py "Drive 2 meters forward then turn left 90 degrees"
```
The CLI reads the prompt, the AI generates a list of actions (drive, turn, pause, etc.) and executes them through `FormDataRobotAPIClient`.

## Testing
```bash
pytest -q
```
Runs `tests/test_robot_scenarios.py` which validates the agent’s prompt‑to‑action translation.

## Project structure
- `main.py` – core agent, tools, and command‑loop.
- `robot_server.py` – example HTTP server for the robot.
- `tests/` – pytest suite.
- `AGENTS.md` – detailed guide for extending the Pydantic AI agent.

## Features
- Natural‑language to robot‑action conversion.
- Optional “fun” stop‑reason mode (`FUN_FEATURES=1`).
- Dynamic stop‑reason generation via a secondary AI agent.
