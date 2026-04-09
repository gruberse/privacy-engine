import uvicorn
from ast import literal_eval
from fastapi import FastAPI, Response, status
from os import mkdir, remove
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from shutil import rmtree
from subprocess import CalledProcessError, run
from sys import exit
from typing import List


class Settings(BaseSettings):
    id: int
    parties: List[str]
    algorithm: str = "replicated"
    n: int
    m: int


class ComputeRequest(BaseModel):
    configurations: List[List[int]]


class ParameterizedComputeRequest(ComputeRequest):
    parameter: int


class MatrixSetup(BaseModel):
    matrix: str


new_env = {"LD_LIBRARY_PATH": ".:$LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH": ".:$DYLD_LIBRARY_PATH"}
app = FastAPI(title="SlotMachine PrivacyEngine Controller")
settings = Settings()


def determine_suffix(m: int):
    if m < 101:
        return 100
    elif m < 201:
        return 200
    elif m < 301:
        return 300
    elif m < 401:
        return 400
    else:
        return 500


def call_mpspdz(program: str, batch: int = 10000):
    if settings.algorithm == "shamir":
        return ["./shamir-party.x", str(settings.id), program, "-ip", "Parties", "-N", "3", "--batch-size", str(batch), "-OF", "out"]
    elif settings.algorithm == "replicated":
        return ["./replicated-field-party.x", "-ip", "Parties", "--batch-size", str(batch), "-OF", "out", "-p", str(settings.id), program]
    else:
        exit(f"unknown algorithm: '{settings.algorithm}'")


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


@app.put("/computeFitnessClear")
async def compute(response: Response, request: ComputeRequest):
    n = len(request.configurations[0])
    m = len(request.configurations)
    size = determine_suffix(m)
    with open(f"Programs/Public-Input/fitness_clear-{size}", 'w') as file:
        try:
            file.write(f"{n}\n")
            file.write(f"{m}\n")
            for conf in request.configurations:
                file.write("\n".join(str(i) for i in conf))
                file.write("\n")
        except OSError as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return e.errno
    try:
        run(call_mpspdz(f"fitness_clear-{size}", m * 10), check=True, env=new_env)
    except CalledProcessError as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return e.returncode
    with open(f"out-P{settings.id}-0") as file:
        res = literal_eval(file.read())[:m]
    remove(f"out-P{settings.id}-0")
    return res


@app.put("/computePopulationOrder")
async def compute2(response: Response, request: ComputeRequest):
    n = len(request.configurations[0])
    m = len(request.configurations)
    size = determine_suffix(m)
    with open(f"Programs/Public-Input/population_order-{size}", 'w') as file:
        try:
            file.write(f"{n}\n")
            file.write(f"{m}\n")
            for conf in request.configurations:
                file.write("\n".join(str(i) for i in conf))
                file.write("\n")
        except OSError as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return e.errno
    try:
        run(call_mpspdz(f"population_order-{size}", m * 2), check=True, env=new_env)
    except CalledProcessError as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return e.returncode
    with open(f"out-P{settings.id}-0") as file:
        lines = file.read().splitlines()
        indices = literal_eval(lines[0])[size - m:]
        max_value = literal_eval(lines[1])
    remove(f"out-P{settings.id}-0")
    return [max_value] + indices


@app.put("/computeClassification")
async def compute3(response: Response, request: ParameterizedComputeRequest):
    n = len(request.configurations[0])
    m = len(request.configurations)
    size = determine_suffix(m)
    with open(f"Programs/Public-Input/classification-{size}", 'w') as file:
        try:
            file.write(f"{request.parameter}\n")
            file.write(f"{n}\n")
            file.write(f"{m}\n")
            for conf in request.configurations:
                file.write("\n".join(str(i) for i in conf))
                file.write("\n")
        except OSError as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return e.errno
    try:
        run(call_mpspdz(f"classification-{size}", m * 4), check=True, env=new_env)
    except CalledProcessError as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return e.returncode
    with open(f"out-P{settings.id}-0") as file:
        lines = file.read().splitlines()
        indices = literal_eval(lines[0])
        max_value = literal_eval(lines[1])
    remove(f"out-P{settings.id}-0")
    return [max_value] + [i for i, x in enumerate(indices) if x]


@app.put("/computeExact")
async def compute4(response: Response):
    try:
        run(call_mpspdz("lap_solver"), check=True, env=new_env)
    except CalledProcessError as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return e.returncode
    with open(f"out-P{settings.id}-0") as file:
        res = literal_eval(file.read())
    remove(f"out-P{settings.id}-0")
    return res


@app.put("/computeMunkres")
async def compute8(response: Response):
    try:
        run(call_mpspdz("munkres"), check=True, env=new_env)
    except CalledProcessError as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return e.returncode
    with open(f"out-P{settings.id}-0") as file:
        res = literal_eval(file.read())
    remove(f"out-P{settings.id}-0")
    return res


@app.put("/computeBuckets")
async def compute5(response: Response, request: ParameterizedComputeRequest):
    n = len(request.configurations[0])
    m = len(request.configurations)
    size = determine_suffix(m)
    with open(f"Programs/Public-Input/buckets-{size}", 'w') as file:
        try:
            file.write(f"{request.parameter}\n")
            file.write(f"{n}\n")
            file.write(f"{m}\n")
            for conf in request.configurations:
                file.write("\n".join(str(i) for i in conf))
                file.write("\n")
        except OSError as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return e.errno
    try:
        run(call_mpspdz(f"buckets-{size}", m * 3), check=True, env=new_env)
    except CalledProcessError as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return e.returncode
    with open(f"out-P{settings.id}-0") as file:
        max_value = int(file.readline())
        res = literal_eval(file.read())[:m]
    remove(f"out-P{settings.id}-0")
    return [max_value] + res


@app.put("/computeQuantiles")
async def compute6(response: Response, request: ParameterizedComputeRequest):
    n = len(request.configurations[0])
    m = len(request.configurations)
    size = determine_suffix(m)
    with open(f"Programs/Public-Input/quantiles-{size}", 'w') as file:
        try:
            file.write(f"{request.parameter}\n")
            file.write(f"{n}\n")
            file.write(f"{m}\n")
            for conf in request.configurations:
                file.write("\n".join(str(i) for i in conf))
                file.write("\n")
        except OSError as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return e.errno
    try:
        run(call_mpspdz(f"quantiles-{size}", m * 10), check=True, env=new_env)
    except CalledProcessError as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return e.returncode
    with open(f"out-P{settings.id}-0") as file:
        max_value = int(file.readline())
        res = literal_eval(file.read())[size - m:]
    remove(f"out-P{settings.id}-0")
    return [max_value] + res


@app.put("/computeTopIndividuals")
async def compute7(response: Response, request: ParameterizedComputeRequest):
    n = len(request.configurations[0])
    m = len(request.configurations)
    size = determine_suffix(m)
    with open(f"Programs/Public-Input/top_individuals-{size}", 'w') as file:
        try:
            file.write(f"{request.parameter}\n")
            file.write(f"{n}\n")
            file.write(f"{m}\n")
            for conf in request.configurations:
                file.write("\n".join(str(i) for i in conf))
                file.write("\n")
        except OSError as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return e.errno
    try:
        run(call_mpspdz(f"top_individuals-{size}", m * 10), check=True, env=new_env)
    except CalledProcessError as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return e.returncode
    with open(f"out-P{settings.id}-0") as file:
        max_value = int(file.readline())
        res = literal_eval(file.read())
    remove(f"out-P{settings.id}-0")
    return [max_value] + res


if __name__ == "__main__":
    if settings.algorithm == "":
        settings.algorithm = "replicated"
    elif settings.algorithm not in ["shamir", "replicated"]:
        exit(f"unknown algorithm: '{settings.algorithm}'")
    rmtree("/Persistence", ignore_errors=True)
    mkdir("/Persistence")
    rmtree("/Programs/Public-Input", ignore_errors=True)
    mkdir("/Programs/Public-Input")
    with open("Parties", 'w') as f:
        f.write("\n".join(s for s in settings.parties))
    uvicorn.run(app, host="0.0.0.0", port=(8420 + settings.id))
