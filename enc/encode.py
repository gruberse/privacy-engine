import uvicorn
from fastapi import Body, FastAPI, HTTPException, status
from os import getenv, remove
from pydantic import BaseModel
from starlette_prometheus import metrics, PrometheusMiddleware
from subprocess import CalledProcessError, run
from sys import exit
from typing import List, Mapping

app = FastAPI()
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)


class Weight(BaseModel):
    slotTime: str
    weight: str


class WeightObject(BaseModel):
    weightMap: List[Weight]


class WeightMap(BaseModel):
    flightId: str
    weightMap: List[Weight]


class EncodedWeightMap(BaseModel):
    flightId: str
    encodedWeights: List[WeightObject]


def split(data: List[int]):
    with open("Player-Data/Input-P0-0", 'w') as file:
        file.write("\n".join(map(str, data)))
    try:
        if algorithm == "shamir":
            run(["Scripts/shamir.sh", "encode"], capture_output=True, check=True)
        elif algorithm == "replicated":
            run(["Scripts/rep-field.sh", "encode"], capture_output=True, check=True)
        else:
            exit(f"unknown algorithm: '{algorithm}'")
    except CalledProcessError as e:
        print(e.returncode)
        print(e.stdout)
        print(e.stderr)
        raise e
    res = []
    for i in [0, 1, 2]:
        with open(f"Persistence/Transactions-P{i}.data", 'rb') as file:
            res.append(file.read().hex())
        remove(f"Persistence/Transactions-P{i}.data")
    return res


@app.put("/", response_model=Mapping[str, str])
async def test(data: List[List[int]] = Body(default=[], example=[[2, 3], [4, 5]])):
    """
    Secret-share a weight-map
    Input is a rectangular matrix
    Output is a map from 'A', 'B', 'C' to shares of the input weight-map
    """
    # keys = ["A", "B", "C"]
    # shared = [split(d) for d in data]
    # res = {k: [] for k in keys}
    # for s in shared:
    #     for k, d in zip(keys, s):
    #         res[k].append(d)
    # return res
    return {k: d for k, d in zip(["A", "B", "C"], split([d for r in data for d in r]))}


@app.put("/encode", responses={200: {"model": EncodedWeightMap}})
async def encode(data: WeightMap):
    """
    Secret-share a WeightMap
    """
    if all([d.weight.isdecimal() for d in data.weightMap]):
        shared = split([int(d.weight) for d in data.weightMap])
        weights = [[], [], []]
        for w, w1, w2, w3 in zip(data.weightMap, shared[0], shared[1], shared[2]):
            weights[0].append(Weight(slotTime=w.slotTime, weight=str(w1)))
            weights[1].append(Weight(slotTime=w.slotTime, weight=str(w2)))
            weights[2].append(Weight(slotTime=w.slotTime, weight=str(w3)))
        weights = [WeightObject(weightMap=weights[0]), WeightObject(weightMap=weights[1]), WeightObject(weightMap=weights[2])]
        res = EncodedWeightMap(flightId=data.flightId, encodedWeights=weights)
        return res
    else:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="not all weights are integer")


if __name__ == "__main__":
    algorithm = getenv("ALGORITHM")
    if algorithm == "":
        algorithm = "replicated"
    elif algorithm not in ["shamir", "replicated"]:
        exit(f"unknown algorithm: '{algorithm}'")
    uvicorn.run(app, host="0.0.0.0", port=8642)
