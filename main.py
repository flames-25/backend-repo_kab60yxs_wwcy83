import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product, Order

app = FastAPI(title="Sportswear Shop API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Sportswear Shop API running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, 'name', None) or "Unknown"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# ---------- Products ----------
@app.post("/api/products", response_model=dict)
async def create_product(product: Product):
    try:
        product_id = create_document("product", product)
        return {"id": product_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products", response_model=List[dict])
async def list_products(category: Optional[str] = None, sport: Optional[str] = None, q: Optional[str] = None):
    try:
        filter_dict = {}
        if category:
            filter_dict["category"] = category
        if sport:
            filter_dict["sport"] = sport
        if q:
            filter_dict["title"] = {"$regex": q, "$options": "i"}
        docs = get_documents("product", filter_dict)
        # Convert ObjectIds
        for d in docs:
            d["id"] = str(d.pop("_id"))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{product_id}", response_model=dict)
async def get_product(product_id: str):
    try:
        doc = db["product"].find_one({"_id": ObjectId(product_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Product not found")
        doc["id"] = str(doc.pop("_id"))
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/products/seed", response_model=dict)
async def seed_products():
    try:
        count = db["product"].count_documents({}) if db is not None else 0
        if count > 0:
            return {"inserted": 0, "message": "Products already exist"}
        demo_products = [
            {
                "title": "AeroRun Pro Tee",
                "description": "Ultra-light breathable running t-shirt.",
                "price": 29.99,
                "category": "Tops",
                "sport": "Running",
                "brand": "Fleet",
                "sizes": ["S","M","L","XL"],
                "colors": ["Black","Neon Green","White"],
                "image": "https://images.unsplash.com/photo-1554344058-0cf8f5d386df?q=80&w=1200&auto=format&fit=crop",
                "in_stock": True,
                "stock": 50
            },
            {
                "title": "FlexStudio Yoga Leggings",
                "description": "High-stretch, squat-proof leggings.",
                "price": 49.0,
                "category": "Bottoms",
                "sport": "Yoga",
                "brand": "ZenMotion",
                "sizes": ["XS","S","M","L"],
                "colors": ["Navy","Burgundy","Charcoal"],
                "image": "https://images.unsplash.com/photo-1549575810-39cc4b3a0224?q=80&w=1200&auto=format&fit=crop",
                "in_stock": True,
                "stock": 35
            },
            {
                "title": "TrailGrip XT Shoes",
                "description": "All-terrain trail running shoes.",
                "price": 95.5,
                "category": "Footwear",
                "sport": "Running",
                "brand": "Peak",
                "sizes": ["7","8","9","10","11"],
                "colors": ["Gray","Orange"],
                "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=1200&auto=format&fit=crop",
                "in_stock": True,
                "stock": 20
            },
            {
                "title": "ProShield Training Jacket",
                "description": "Wind-resistant, water-repellent shell.",
                "price": 79.0,
                "category": "Outerwear",
                "sport": "Football",
                "brand": "Gridiron",
                "sizes": ["M","L","XL"],
                "colors": ["Olive","Black"],
                "image": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?q=80&w=1200&auto=format&fit=crop",
                "in_stock": True,
                "stock": 15
            }
        ]
        inserted = 0
        for p in demo_products:
            create_document("product", p)
            inserted += 1
        return {"inserted": inserted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Orders ----------
@app.post("/api/orders", response_model=dict)
async def create_order(order: Order):
    try:
        order_id = create_document("order", order)
        return {"id": order_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders", response_model=List[dict])
async def list_orders():
    try:
        docs = get_documents("order")
        for d in docs:
            d["id"] = str(d.pop("_id"))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
