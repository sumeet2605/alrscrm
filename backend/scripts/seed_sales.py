from app.core.database import SessionLocal
from app.sales.seeds import seed_sales


def main() -> None:
    db = SessionLocal()
    try:
        seed_sales(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
