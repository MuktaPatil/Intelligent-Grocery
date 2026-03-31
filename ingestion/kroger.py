import os
import base64
import requests
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID     = os.getenv("KROGER_CLIENT_ID").strip()
CLIENT_SECRET = os.getenv("KROGER_CLIENT_SECRET").strip()
BASE_URL      = "https://api.kroger.com/v1"

# ── Auth ──────────────────────────────────────────────────────────────────────

def get_access_token(scope=None):
    """Client credentials OAuth2 flow."""
    encoded_id     = quote(CLIENT_ID, safe="")
    encoded_secret = quote(CLIENT_SECRET, safe="")
    creds = base64.b64encode(f"{encoded_id}:{encoded_secret}".encode()).decode()
    data  = {"grant_type": "client_credentials"}
    if scope:
        data["scope"] = scope
    resp = requests.post(
        f"{BASE_URL}/connect/oauth2/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {creds}"
        },
        data=data
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


# ── Locations ─────────────────────────────────────────────────────────────────

def get_location_id(token, zip_code="75201"):
    """Get nearest Kroger store ID for a given zip. 75201 = Dallas, TX."""
    resp = requests.get(
        f"{BASE_URL}/locations",
        headers={"Authorization": f"bearer {token}"},
        params={"filter.zipCode.near": zip_code, "filter.limit": 1}
    )
    resp.raise_for_status()
    locations = resp.json().get("data", [])
    if not locations:
        raise ValueError(f"No Kroger locations found near {zip_code}")
    loc = locations[0]
    print(f"Using store: {loc['name']} — {loc['address']['addressLine1']}")
    return loc["locationId"]


# ── Products ──────────────────────────────────────────────────────────────────

ITEMS = [
    "milk", "eggs", "bread", "rice", "chicken breast",
    "pasta", "butter", "orange juice", "bananas", "yogurt",
    "canned tomatoes", "olive oil", "ground beef", "apples", "cheese"
]

def get_prices(token, location_id, search_term, limit=3):
    """Search for a product and return top results with price info."""
    resp = requests.get(
        f"{BASE_URL}/products",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "filter.term":       search_term,
            "filter.locationId": location_id,
            "filter.limit":      limit
        }
    )
    if resp.status_code != 200:
        print(f"  ⚠ Products API error {resp.status_code}: {resp.text[:200]}")
    resp.raise_for_status()

    products = resp.json().get("data", [])
    results  = []
    for p in products:
        price_info = p.get("items", [{}])[0]
        price      = price_info.get("price", {}).get("regular")
        size       = price_info.get("size", "unknown")
        results.append({
            "search_term": search_term,
            "product_id":  p.get("productId"),
            "description": p.get("description"),
            "brand":       p.get("brand"),
            "size":        size,
            "price":       price,
            "location_id": location_id
        })
    return results


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from db.database import save_store, save_prices

    token_locations = get_access_token()
    token_products  = get_access_token(scope="product.compact")
    location_id     = get_location_id(token_locations)

    # save store to db
    save_store(location_id, "Kroger Fresh Fare - Capitol Ave", "4241 Capitol Ave")

    all_products = []
    for item in ITEMS:
        print(f"Fetching: {item}")
        results = get_prices(token_products, location_id, item)
        all_products.extend(results)

    save_prices(all_products)
    print(f"\nDone! {len(all_products)} products saved to database.")