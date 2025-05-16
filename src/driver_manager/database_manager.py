from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from driver_manager.models import Base, Driver, DriverHistory

engine = create_engine("sqlite:///drivers.db")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def delete_db():
    Base.metadata.drop_all(bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


# Update or create driver
def upsert_driver(driver_id: str, location: tuple[int, int]) -> dict:
    session = SessionLocal()
    try:
        driver = session.query(Driver).filter(Driver.id == driver_id).first()
        if driver:
            driver.latitude = location[0]
            driver.longitude = location[1]
            return_value = {"success": True, "msg": "Driver updated"}
        else:
            driver = Driver(id=driver_id, latitude=location[0], longitude=location[1])
            session.add(driver)
            return_value = {"success": True, "msg": "Driver created"}
        session.add(
            DriverHistory(
                driver_id=driver.id,
                latitude=driver.latitude,
                longitude=driver.longitude,
            )
        )
        session.commit()
    except Exception as e:
        session.rollback()
        return_value = {"success": False, "msg": "Error: " + str(e)}
    finally:
        session.close()
        return return_value


def remove_driver(driver_id: str) -> dict:
    session = SessionLocal()
    try:
        driver = session.query(Driver).filter(Driver.id == driver_id).first()
        driver_history = (
            session.query(DriverHistory)
            .filter(DriverHistory.driver_id == driver_id)
            .all()
        )
        if driver:
            session.delete(driver)
            for history in driver_history:
                session.delete(history)
            session.commit()
            return_value = {"success": True, "msg": "Driver deleted"}
        else:
            return_value = {"success": False, "msg": "Driver not found"}
    except Exception as e:
        session.rollback()
        return_value = {"success": False, "msg": "Error: " + str(e)}
    finally:
        session.close()
        return return_value


def get_all_drivers() -> dict:
    session = SessionLocal()
    try:
        drivers = session.query(Driver).all()
        return_value = {
            "success": True,
            "query_result": drivers,
            "msg": "Driver list retrieved",
        }
    except Exception as e:
        return_value = {"success": False, "msg": "Error: " + str(e)}
    finally:
        session.close()
        return return_value
