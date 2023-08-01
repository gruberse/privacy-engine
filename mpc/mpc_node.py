import os

import uvicorn
from ast import literal_eval
from fastapi import FastAPI, Response, status
from os import remove
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from subprocess import CalledProcessError, run
from typing import List


class Settings(BaseSettings):
    id: int
    parties: List[str]


class ComputeRequest(BaseModel):
    configurations: List[List[int]]


class MatrixSetup(BaseModel):
    matrix: str


app = FastAPI(title="SlotMachine PrivacyEngine Controller")
settings = Settings()


@app.get("/status")
async def get_status():
    return


@app.put("/session", status_code=status.HTTP_201_CREATED)
async def create_session(response: Response, request: MatrixSetup):
    with open(f"Persistence/Transactions-P{settings.id}.data", 'wb') as file:
        try:
            file.write(bytes.fromhex(request.matrix))
        except OSError as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return e.errno
    return


@app.put("/computeFitnessClear")
async def compute(response: Response, request: ComputeRequest):
    with open("Programs/Public-Input/fitness_clear", 'w') as file:
        try:
            for conf in request.configurations:
                file.write("\n".join(str(i) for i in conf))
                file.write("\n")
        except OSError as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return e.errno
    try:
        new_env = {"LD_LIBRARY_PATH": ".:$LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH": ".:$DYLD_LIBRARY_PATH"}
        line = ["./shamir-party.x", str(settings.id), "fitness_clear", "-ip", "Parties", "-N", "3", "-OF", "out"]
        run(line, check=True, env=new_env)
    except CalledProcessError as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return e.returncode
    with open(f"out-P{settings.id}-0") as file:
        res = literal_eval(file.read())
    remove(f"out-P{settings.id}-0")
    return res


@app.put("/computePopulationOrder")
async def compute2(response: Response, request: ComputeRequest):
    with open(f"Programs/Public-Input/population_order", 'w') as file:
        try:
            for conf in request.configurations:
                file.write("\n".join(str(i) for i in conf))
                file.write("\n")
        except OSError as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return e.errno
    try:
        new_env = {"LD_LIBRARY_PATH": ".:$LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH": ".:$DYLD_LIBRARY_PATH"}
        line = ["./shamir-party.x", str(settings.id), "population_order", "-ip", "Parties", "-N", "3", "-OF", "out"]
        run(line, check=True, env=new_env)
    except CalledProcessError as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return e.returncode
    with open(f"out-P{settings.id}-0") as file:
        lines = file.read().splitlines()
        indices = literal_eval(lines[0])
        max_value = literal_eval(lines[1])
    remove(f"out-P{settings.id}-0")
    return [max_value] + indices


@app.put("/computeClassification")
async def compute3(response: Response, request: ComputeRequest):
    with open(f"Programs/Public-Input/classification", 'w') as file:
        try:
            for conf in request.configurations:
                file.write("\n".join(str(i) for i in conf))
                file.write("\n")
        except OSError as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return e.errno
    try:
        new_env = {"LD_LIBRARY_PATH": ".:$LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH": ".:$DYLD_LIBRARY_PATH"}
        line = ["./shamir-party.x", str(settings.id), "classification", "-ip", "Parties", "-N", "3", "-OF", "out"]
        run(line, check=True, env=new_env)
    except CalledProcessError as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return e.returncode
    with open(f"out-P{settings.id}-0") as file:
        res = literal_eval(file.read())
    remove(f"out-P{settings.id}-0")
    return [i for i, x in enumerate(res) if x]

if __name__ == "__main__":
    os.mkdir("/Persistence")
    os.mkdir("/Programs/Public-Input")
    with open(f"Parties", 'w') as f:
        f.write("\n".join(s for s in settings.parties))
    uvicorn.run(app, host="0.0.0.0", port=8000)
