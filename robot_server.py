from fastapi import FastAPI, HTTPException
from typing import List, Literal
from pydantic import BaseModel

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
app = FastAPI(title="Robot Control API")

# Simple robot controller stub (replace with real implementation)
class RobotController:
    @classmethod
    async def drive(cls, distance: float, direction: str) -> str:
        return f"Driving {distance} meters {direction}."

    @classmethod
    async def turn_left(cls, degrees: int) -> str:
        return f"Turning left {degrees}\u00b0."

    @classmethod
    async def turn_right(cls, degrees: int) -> str:
        return f"Turning right {degrees}\u00b0."

    @classmethod
    async def stop(cls) -> str:
        return "Stopping robot."

    @classmethod
    async def follow_line(cls) -> str:
        return "Following line."

# Request models
class DriveRequest(BaseModel):
    distance: float
    direction: str  # "forward" or "backward"

class TurnRequest(BaseModel):
    degrees: Literal[90]

class SpinRequest(BaseModel):
    duration: float

# Endpoints return a simple JSON with a single "result" field
@app.get("/drive")
async def drive(direction: str, duration: int):
    logger.debug(f"/drive called with direction={direction}, duration={duration}")
    # Return structured action matching RobotOutput schema
    distance = duration / 1000.0
    return {"actions": [{"command": "drive", "distance": distance, "direction": direction}]}




@app.get("/pause")
async def pause(duration: int = 0):
    logger.debug(f"/pause called with duration={duration}")
    # Return structured action matching RobotOutput schema
    return {"actions": [{"command": "pause", "duration": duration / 1000.0}]}

@app.get("/follow_line")
async def follow_line():
    logger.debug("/follow_line called")
    # Return structured action matching RobotOutput schema
    return {"actions": [{"command": "follow_line"}]}


@app.get("/spin")
async def spin(duration: int):
    logger.debug(f"/spin called with duration={duration}")
    # Return structured action matching RobotOutput schema
    return {"actions": [{"command": "spin", "duration": duration / 1000.0}]}

@app.get("/turn")
async def turn(direction: str, degree: int):
    logger.debug(f"/turn called with direction={direction}, degree={degree}")
    if direction == "left":
        cmd = "turn_left"
    elif direction == "right":
        cmd = "turn_right"
    else:
        raise HTTPException(status_code=400, detail="Invalid direction")
    return {"actions": [{"command": cmd, "degrees": degree}]}
