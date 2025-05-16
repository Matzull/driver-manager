import math
from fastapi import FastAPI
from pydantic import BaseModel, field_validator
from fastapi.responses import JSONResponse
from driver_manager.database_manager import get_all_drivers, upsert_driver, remove_driver, init_db

init_db()


class Driver(BaseModel):
    driver_id: str
    position: tuple[int, int]

    # The driver id must not be empty
    @field_validator("driver_id")
    def check_driver_id(cls, v):
        if not v:
            raise ValueError("Driver ID cannot be empty")
        return v


app = FastAPI()


@app.put("/update-position/")
def update_driver_position(driver: Driver):
    res = upsert_driver(driver_id=driver.driver_id, location=driver.position)
    success = res.get("success")
    result = res.get("msg")

    if success:
        return JSONResponse(content={"result": result}, status_code=200)
    else:
        return JSONResponse(content={"error": result}, status_code=500)


@app.delete("/stop-tracking/")
def stop_tracking(driver_id: str):
    res = remove_driver(driver_id)
    success = res.get("success")
    result = res.get("msg")

    if success:
        return JSONResponse(content={"result": result}, status_code=200)
    else:
        return JSONResponse(content={"error": result}, status_code=500)


@app.post("/get-closest-driver/")
def get_closest_driver(position: tuple[int, int]):
    res = get_all_drivers()
    success = res.get("success")
    result = res.get("msg")
    drivers = res.get("query_result")

    if not success:
        return JSONResponse(content={"error": result}, status_code=500)
    if not drivers:
        return JSONResponse(content={"result": "No drivers found"}, status_code=200)

    def euclidean_distance(coord1, coord2):
        return math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)

    closest_driver = min(
        drivers,
        key=lambda driver: euclidean_distance(
            position, (driver.latitude, driver.longitude)
        ),
    )
    min_distance = euclidean_distance(
        position, (closest_driver.latitude, closest_driver.longitude)
    )
    print(closest_driver.id)
    return JSONResponse(
        content={
            "result": f"Found driver {closest_driver.id} in position{closest_driver.latitude, closest_driver.longitude} distance is {min_distance:.2f}"
        },
        status_code=200,
    )
