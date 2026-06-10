from app.core.database import SessionLocal
from app.identity.seeds import seed_identity


def main() -> None:
    db = SessionLocal()
    try:
        seed_identity(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
