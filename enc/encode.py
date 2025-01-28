import uvicorn
from fastapi import Body, FastAPI, HTTPException, status
from os import getenv, remove
from starlette_prometheus import metrics, PrometheusMiddleware
from subprocess import CalledProcessError, run
from sys import exit
from typing import List, Mapping

app = FastAPI()
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)

N = int(getenv("n"))


def split(data: List[List[int]]):
    width = len(data[0])
    if any([len(r) != width for r in data]):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="input matrix is not rectangular")
    if len(data) > N or width > N:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"input matrix is bigger than preconfigured maximum of {N}x{N}")
    with open("Player-Data/Input-P0-0", 'w') as file:
        for row in data:
            row = [str(int(v)) for v in row]
            file.write(" ".join(row + (["0"] * (N - width))))
            file.write("\n")
        for _ in range(N - len(data)):
            file.write(" ".join(["0"] * N))
            file.write("\n")
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
    return {k: d for k, d in zip(["A", "B", "C"], split(data))}


if __name__ == "__main__":
    algorithm = getenv("ALGORITHM")
    if algorithm == "":
        algorithm = "replicated"
    elif algorithm not in ["shamir", "replicated"]:
        exit(f"unknown algorithm: '{algorithm}'")
    uvicorn.run(app, host="0.0.0.0", port=8642)
