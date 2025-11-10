from asyncio import gather

import uvicorn
from fastapi import Body, FastAPI, Response, status
from httpx import AsyncClient, put, ReadTimeout
from json.decoder import JSONDecodeError
from pydantic import BaseModel, Field, AnyUrl
from pydantic_settings import BaseSettings
from starlette_prometheus import metrics, PrometheusMiddleware
from typing import List, Mapping, Tuple

client = AsyncClient()


class Settings(BaseSettings):
    encoder: AnyUrl
    peers: Mapping[str, AnyUrl]


class Error(BaseModel):
    code: int = Field(title="An HTTP status code")
    message: str = Field(title="A detailed error message")


class AirlineMapping(BaseModel):
    mapping: Mapping[str, List[int]] = Field(
        title="A mapping from airlines to their flights",
        example={"A": [0, 1], "B": [2, 3]})


class PlainTextSetup(AirlineMapping):
    weights: List[List[int]] = Field(
        title="A square matrix of integer-valued weights; each flight is one row; each slot is one column",
        example=[[2, 3], [4, 5]])


class SecretSharedSetup(AirlineMapping):
    weights: Mapping[str, str] = Field(
        title="A mapping of secret-shared integer-valued square matrices to each of the MPC nodes",
        example={"A": [[45, 32], [91, 34]], "B": [[98, 23], [12, 9]], "C": [[76, 42], [99, 58]]})


class MaxOrderedResponse(BaseModel):
    maximum: int = Field(title="The highest fitness value")
    order: List[int] = Field(title="Indices, ordered from highest to lowest")


class ClassificationResponse(BaseModel):
    highest: int = Field(title="The index of the configuration with the highest fitness")
    best: bool = Field(title="Is the highest fitness value also the best so far in this run?")
    indices: List[int] = Field(title="Indices of configurations exceeding the threshold")


class BucketQuantileResponse(BaseModel):
    maximum: int = Field(title="The highest fitness value")
    mapping: List[int] = Field(title="List associating the index of each input configuration to a bucket/quantile")


class ClearingRequest(BaseModel):
    data: List[int] = Field(title="A configuration", example=[1, 0])


class ClearingResponse(BaseModel):
    values: Mapping[str, int]


app = FastAPI(title="SlotMachine PrivacyEngine Controller")
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)
settings = Settings()
mapping: Mapping[str, List[int]] = {}


@app.put("/sessionClear", status_code=status.HTTP_201_CREATED,
         summary="Create a new session with plain-text data",
         tags=["test-only"],
         responses={400: {"model": Error}, 500: {"model": Error}, 503: {"model": Error}})
async def create_session_clear(response: Response, request: PlainTextSetup):
    """
    Create a new session using a clear-text weight-map
    The weight-map is a rectangular matrix (list of lists)
    """
    flattened = [y for x in request.mapping.values() for y in x]
    if not sorted(flattened) == list(range(len(flattened))):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return Error(code=400, message="malformed mapping")
    global mapping
    mapping = request.mapping
    res = put(str(settings.encoder), json=request.weights)
    if res.status_code != 200:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Error(code=500, message=f"Got {res.status_code} from Encoder Service")
    try:
        shared = res.json()
    except JSONDecodeError as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Error(code=500, message=e.msg)
    ret = []
    for k, url in settings.peers.items():
        ret.append(client.put(str(url) + "session", json={'matrix': shared[k]}))
    try:
        ret = await gather(*ret)
    except ReadTimeout:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Error(code=500, message="timeout on one of the MPC nodes")
    if all(r.status_code == 201 for r in ret):
        return
    else:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return Error(code=503, message="Could not query MPC ports")


@app.get("/nodes", tags=["info"])
async def get_nodes():
    return list(settings.peers.values())


@app.get("/status", responses={500: {"model": Error}, 503: {"model": Error}}, tags=["info"])
async def get_status(response: Response):
    ret = []
    for k, url in settings.peers.items():
        ret.append(client.get(str(url) + "status"))
    try:
        ret = await gather(*ret)
    except ReadTimeout:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Error(code=500, message="timeout on one of the MPC nodes")
    if any(r.status_code != 200 for r in ret):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return Error(code=503, message="MPC node unavailable")


@app.put("/sessionSecret", status_code=status.HTTP_201_CREATED,
         summary="Create a new session with secret-shared data",
         tags=["secret-shared"],
         responses={400: {"model": Error}, 500: {"model": Error}, 503: {"model": Error}})
async def create_session_secret(response: Response, request: SecretSharedSetup):
    """
    Create a new session using secret-shared weight-maps (one for each MPC node)
    The weight-map is a dictionary, containing for each MPC node ("peer") a rectangular matrix (list of lists)
    """
    if request.weights.keys() != settings.peers.keys():
        response.status_code = status.HTTP_400_BAD_REQUEST
        return Error(code=400, message="must provide data for all nodes")
    flattened = [y for x in request.mapping.values() for y in x]
    if not sorted(flattened) == list(range(len(flattened))):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return Error(code=400, message="malformed mapping")
    global mapping
    mapping = request.mapping
    ret = []
    for k, v in request.weights.items():
        ret.append(client.put(str(settings.peers[k]) + "session", json={'matrix': v}))
    try:
        ret = await gather(*ret)
    except ReadTimeout:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Error(code=500, message="timeout on one of the MPC nodes")
    if any(r.status_code != 201 for r in ret):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return Error(code=503, message="MPC node unavailable")


@app.put("/computeFitnessClear",
         summary="Compute and output a fitness value",
         tags=["test-only"],
         responses={200: {"model": List[int]}, 400: {"model": Error}, 500: {"model": Error}})
async def compute_fitness_clear(
        response: Response,
        data: List[List[int]] = Body(example=[[0, 1], [1, 0]])):
    """
    Return a list of clear-text fitness value for a given list of configuration.
    For a weight-map [[12, 13], [23, 34]], an input of [[0, 1], [1, 0]] should return [46, 36].
    """
    size = len(data)
    if size == 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return Error(code=400, message="no data")
    length = len(data[0])
    if not all([len(d) == length for d in data[1:]]):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return Error(code=400, message="wrong data")
    ret = []
    for k, url in settings.peers.items():
        ret.append(client.put(str(url) + "computeFitnessClear", json={'configurations': data}))
    try:
        ret = await gather(*ret)
    except ReadTimeout:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Error(code=500, message="timeout on one of the MPC nodes")
    res = ret[0]
    if all(r.status_code == 200 for r in ret):
        return res.json()
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Error(code=500, message=f"unexpected error: {res}")


@app.put("/computePopulationOrder",
         summary="Compute a population order",
         tags=["secret-shared"],
         responses={200: {"model": MaxOrderedResponse},
                    400: {"model": Error}, 500: {"model": Error}})
async def compute_population_order(
        response: Response,
        data: List[List[int]] = Body(example=[[1, 0], [0, 1]])):
    """
    Return the maximum fitness value and an ordered list of configurations.
    For a weight-map [[12, 13], [23, 34]], an input of [[0, 1], [1, 0]] should return a maximum of 46 and a list [0, 1].
    """
    size = len(data)
    if size == 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return Error(code=400, message="no data")
    length = len(data[0])
    if not all([len(d) == length for d in data[1:]]):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return Error(code=400, message="wrong data")
    ret = []
    for k, url in settings.peers.items():
        ret.append(client.put(str(url) + "computePopulationOrder", json={'configurations': data}, timeout=300.0))
    try:
        ret = await gather(*ret)
    except ReadTimeout:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Error(code=500, message="timeout on one of the MPC nodes")
    res = ret[0]
    if all(r.status_code == 200 for r in ret):
        indices = res.json()
        return MaxOrderedResponse(maximum=indices[0], order=indices[1:])
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Error(code=500, message=f"unexpected error: {res}")


@app.put("/computeClassification/{threshold}",
         summary="Classify a population",
         tags=["secret-shared"],
         responses={200: {"model": ClassificationResponse},
                    400: {"model": Error}, 500: {"model": Error}})
async def compute_classification(
        response: Response,
        threshold: int,
        data: List[List[int]] = Body(example=[[0, 1], [1, 0]])):
    """
    Return an unordered list of configurations that exceed a desired threshold
    """
    size = len(data)
    if size == 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return Error(code=400, message="no data")
    length = len(data[0])
    if not all([len(d) == length for d in data[1:]]):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return Error(code=400, message="wrong data")
    ret = []
    for k, url in settings.peers.items():
        ret.append(client.put(str(url) + "computeClassification", json={'parameter': threshold,'configurations': data}, timeout=300.0))
    try:
        ret = await gather(*ret)
    except ReadTimeout:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Error(code=500, message="timeout on one of the MPC nodes")
    res = ret[0]
    if all(r.status_code == 200 for r in ret):
        indices = res.json()
        if len(indices) < 4:
            return await compute_top_individuals(response, 3, data)
        # TODO return ClassificationResponse(highest=values[0], best=bool(values[1]), indices=values[2:])
        return ClassificationResponse(highest=indices[0], best=False, indices=indices[1:])
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Error(code=500, message=f"unexpected error: {res}")


@app.put("/computeBuckets/{count}",
         summary="",
         tags=["secret-shared"],
         responses={200: {"model": BucketQuantileResponse},
                    400: {"model": Error}, 500: {"model": Error}})
async def compute_buckets(
        response: Response,
        count: int,
        data: List[List[int]] = Body(example=[[0, 1], [1, 0]])):
    """
    Return a list, associating each input configuration to a bucket
    """
    size = len(data)
    if size == 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return Error(code=400, message="no data")
    length = len(data[0])
    if not all([len(d) == length for d in data[1:]]):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return Error(code=400, message="wrong data")
    ret = []
    for k, url in settings.peers.items():
        ret.append(client.put(str(url) + "computeBuckets", json={'parameter': count, 'configurations': data}, timeout=300.0))
    try:
        ret = await gather(*ret)
    except ReadTimeout:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Error(code=500, message="timeout on one of the MPC nodes")
    res = ret[0]
    if all(r.status_code == 200 for r in ret):
        res = res.json()
        return BucketQuantileResponse(maximum=res[0], mapping=res[1:])
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Error(code=500, message=f"unexpected error: {res}")


@app.put("/computeQuantiles/{count}",
         summary="",
         tags=["secret-shared"],
         responses={200: {"model": BucketQuantileResponse},
                    400: {"model": Error}, 500: {"model": Error}})
async def compute_quantiles(
        response: Response,
        count: int,
        data: List[List[int]] = Body(example=[[0, 1], [1, 0]])):
    """
    Return a list, associating each input configuration to a quantile
    """
    size = len(data)
    if size == 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return Error(code=400, message="no data")
    length = len(data[0])
    if not all([len(d) == length for d in data[1:]]):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return Error(code=400, message="wrong data")
    ret = []
    for k, url in settings.peers.items():
        ret.append(client.put(str(url) + "computeQuantiles", json={'parameter': count, 'configurations': data}, timeout=300.0))
    try:
        ret = await gather(*ret)
    except ReadTimeout:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Error(code=500, message="timeout on one of the MPC nodes")
    res = ret[0]
    if all(r.status_code == 200 for r in ret):
        res = res.json()
        return BucketQuantileResponse(maximum=res[0], mapping=res[1:])
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Error(code=500, message=f"unexpected error: {res}")


@app.put("/computeTopIndividuals/{count}",
         summary="",
         tags=["secret-shared"],
         responses={200: {"model": ClassificationResponse},
                    400: {"model": Error}, 500: {"model": Error}})
async def compute_top_individuals(
        response: Response,
        count: int,
        data: List[List[int]] = Body(example=[[0, 1], [1, 0]])):
    """
    Return a lexically sorted list of top configurations
    """
    size = len(data)
    if size == 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return Error(code=400, message="no data")
    length = len(data[0])
    if not all([len(d) == length for d in data[1:]]):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return Error(code=400, message="wrong data")
    ret = []
    for k, url in settings.peers.items():
        ret.append(client.put(str(url) + "computeTopIndividuals", json={'parameter': count, 'configurations': data},
                              timeout=300.0))
    try:
        ret = await gather(*ret)
    except ReadTimeout:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Error(code=500, message="timeout on one of the MPC nodes")
    res = ret[0]
    if all(r.status_code == 200 for r in ret):
        indices = res.json()
        # TODO return ClassificationResponse(highest=values[0], best=bool(values[1]), indices=values[2:])
        return ClassificationResponse(highest=indices[0], best=False, indices=sorted([i-1 for i in indices[1:] if i != 0]))
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Error(code=500, message=f"unexpected error: {res}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
