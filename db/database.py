import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DB_NAME     = os.getenv("DB_NAME")
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", "5432")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)


def get_engine():
    return engine


def save_store(location_id, name, address, city="Dallas", state="TX", zip_code="75201"):
    """Upsert store info."""
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO stores (location_id, name, address, city, state, zip_code)
            VALUES (:location_id, :name, :address, :city, :state, :zip_code)
            ON CONFLICT (location_id) DO NOTHING
        """), {
            "location_id": location_id,
            "name":        name,
            "address":     address,
            "city":        city,
            "state":       state,
            "zip_code":    zip_code
        })
        conn.commit()
    print(f"Store saved: {name}")


def save_prices(products: list):
    """Bulk insert product price snapshots."""
    with engine.connect() as conn:
        for p in products:
            conn.execute(text("""
                INSERT INTO prices 
                    (product_id, search_term, description, brand, size, price, location_id)
                VALUES 
                    (:product_id, :search_term, :description, :brand, :size, :price, :location_id)
            """), {
                "product_id":  p.get("product_id"),
                "search_term": p.get("search_term"),
                "description": p.get("description"),
                "brand":       p.get("brand"),
                "size":        p.get("size"),
                "price":       p.get("price"),
                "location_id": p.get("location_id")
            })
        conn.commit()
    print(f"Saved {len(products)} price records.")


if __name__ == "__main__":
    # quick connection test
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        print(result.fetchone())