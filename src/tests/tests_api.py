import pytest
from fastapi.testclient import TestClient
from driver_manager.main import app
from driver_manager.database_manager import delete_db, init_db
from concurrent.futures import ThreadPoolExecutor


client = TestClient(app)


# Reset the database before each test
@pytest.fixture(autouse=True)
def setup_and_teardown():
    delete_db()
    init_db()
    yield
    delete_db()


def test_create_driver_success():
    response = client.put(
        "/update-position/", json={"driver_id": "d1", "position": [0, 0]}
    )
    assert response.status_code == 200
    assert "created" in response.json()["result"].lower()


def test_update_driver_success():
    client.put("/update-position/", json={"driver_id": "d2", "position": [1, 1]})
    response = client.put(
        "/update-position/", json={"driver_id": "d2", "position": [2, 2]}
    )
    assert response.status_code == 200
    assert "updated" in response.json()["result"].lower()


def test_create_driver_without_position():
    response = client.put(
        "/update-position/", json={"driver_id": "d3", "position": None}
    )
    assert response.status_code == 422


def test_update_driver_invalid_position():
    response = client.put(
        "/update-position/", json={"driver_id": "d4", "position": ["a", "b"]}
    )
    assert response.status_code == 500 or response.status_code == 422


def test_update_driver_empty_id():
    response = client.put(
        "/update-position/", json={"driver_id": "", "position": [1, 1]}
    )
    assert response.status_code == 422


def test_stop_tracking_existing_driver():
    client.put("/update-position/", json={"driver_id": "d5", "position": [5, 5]})
    response = client.delete("/stop-tracking/", params={"driver_id": "d5"})
    assert response.status_code == 200
    assert "deleted" in response.json()["result"].lower()


def test_stop_tracking_nonexistent_driver():
    response = client.delete("/stop-tracking/", params={"driver_id": "noexiste"})
    assert response.status_code == 500
    assert "not found" in response.json()["error"].lower()


def test_stop_tracking_empty_id():
    response = client.delete("/stop-tracking/", params={"driver_id": ""})
    assert response.status_code == 500 or response.status_code == 422


def test_get_closest_driver_empty_db():
    response = client.post("/get-closest-driver/", json=[0, 0])
    assert response.status_code == 200
    assert "no drivers found" in response.json()["result"].lower()


def test_get_closest_driver_found():
    client.put("/update-position/", json={"driver_id": "dc1", "position": [1, 1]})
    client.put("/update-position/", json={"driver_id": "dc2", "position": [10, 10]})
    response = client.post("/get-closest-driver/", json=[2, 2])
    assert response.status_code == 200
    assert "found driver dc1" in response.json()["result"].lower()


def test_get_closest_driver_invalid_position():
    response = client.post("/get-closest-driver/", json=["a", "b"])
    assert response.status_code == 422


def test_get_closest_driver_far_position():
    client.put("/update-position/", json={"driver_id": "dc3", "position": [0, 0]})
    response = client.post("/get-closest-driver/", json=[10000, 10000])
    assert response.status_code == 200


def test_create_driver_special_id_chars():
    special_id = "driver-øç√™✓"
    response = client.put(
        "/update-position/", json={"driver_id": special_id, "position": [1, 1]}
    )
    assert response.status_code == 200


def test_multiple_updates():
    driver_id = "dmult"
    for i in range(5):
        response = client.put(
            "/update-position/", json={"driver_id": driver_id, "position": [i, i]}
        )
        assert response.status_code == 200


def test_repeated_stop_tracking():
    driver_id = "drepeat"
    client.put("/update-position/", json={"driver_id": driver_id, "position": [1, 1]})
    response1 = client.delete("/stop-tracking/", params={"driver_id": driver_id})
    response2 = client.delete("/stop-tracking/", params={"driver_id": driver_id})
    assert response1.status_code == 200
    assert response2.status_code == 500


def test_response_json_structure():
    driver_id = "djson"
    pos = [4, 4]
    client.put("/update-position/", json={"driver_id": driver_id, "position": pos})
    response = client.post("/get-closest-driver/", json=pos)
    json_resp = response.json()
    assert "result" in json_resp
    assert isinstance(json_resp["result"], str)


def test_bulk_create_search():
    for i in range(20):
        client.put("/update-position/", json={"driver_id": f"d{i}", "position": [i, i]})
    response = client.post("/get-closest-driver/", json=[10, 11])
    assert response.status_code == 200
    for i in range(20):
        client.delete("/stop-tracking/", params={"driver_id": f"d{i}"})


def test_malformed_json():
    response = client.put("/update-position/", data="not json")
    assert response.status_code == 422


def test_empty_json_put():
    response = client.put("/update-position/", json={})
    assert response.status_code == 422


def test_empty_json_post():
    response = client.post("/get-closest-driver/", json=[])
    assert response.status_code == 422


def test_empty_params_delete():
    response = client.delete("/stop-tracking/")
    assert response.status_code == 422


def test_extra_params_delete():
    response = client.delete(
        "/stop-tracking/", params={"driver_id": "d1", "extra": "param"}
    )
    assert response.status_code == 500


def test_wrong_method_use():
    response = client.get("/update-position/")
    assert response.status_code == 405


def test_wrong_type_params():
    response = client.post(
        "/get-closest-driver/", json={"latitude": "a", "longitude": "b"}
    )
    assert response.status_code == 422


# Stress test for concurrent requests
def test_concurrent_create_delete():
    def create_driver(i):
        return client.put(
            "/update-position/", json={"driver_id": f"concur{i}", "position": [i, i]}
        )

    def delete_driver(i):
        return client.delete("/stop-tracking/", params={"driver_id": f"concur{i}"})

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(create_driver, range(10)))
        for r in results:
            assert r.status_code == 200
        results = list(executor.map(delete_driver, range(10)))
        for r in results:
            assert r.status_code in (200, 500)
