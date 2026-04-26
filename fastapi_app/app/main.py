"""
FastAPI Benchmark Application - Main entry point
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
import asyncio
import logging

from .database import engine, get_db, Base
from .models import Item
from .schemas import ItemCreate, ItemUpdate, ItemResponse, HealthResponse
from .config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="High-performance REST API for benchmarking",
    version=settings.app_version,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Initialize database tables on startup"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully")


@app.on_event("shutdown")
async def shutdown():
    """Close database connections on shutdown"""
    await engine.dispose()
    logger.info("Database connections closed")


# ============= API Endpoints =============

@app.get(
    "/api/items/",
    response_model=List[ItemResponse],
    tags=["items"],
    summary="List items"
)
async def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    in_stock: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
) -> List[ItemResponse]:
    """Retrieve list of items with pagination"""
    query = select(Item)
    
    if category:
        query = query.where(Item.category == category)
    if in_stock is not None:
        query = query.where(Item.in_stock == in_stock)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()
    
    return [ItemResponse.model_validate(item) for item in items]


@app.post(
    "/api/items/",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["items"]
)
async def create_item(
    item: ItemCreate,
    db: AsyncSession = Depends(get_db)
) -> ItemResponse:
    """Create a new item"""
    from datetime import datetime
    now = datetime.utcnow()
    
    db_item = Item(
        name=item.name,
        description=item.description,
        price=item.price,
        in_stock=item.in_stock,
        category=item.category,
        created_at=now,
        updated_at=now
    )
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    
    logger.info(f"Created item with id={db_item.id}")
    return ItemResponse.model_validate(db_item)


@app.get(
    "/api/items/{item_id}",
    response_model=ItemResponse,
    tags=["items"]
)
async def get_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
) -> ItemResponse:
    """Retrieve a specific item by ID"""
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    return ItemResponse.model_validate(item)


@app.put(
    "/api/items/{item_id}",
    response_model=ItemResponse,
    tags=["items"]
)
async def update_item(
    item_id: int,
    item_update: ItemUpdate,
    db: AsyncSession = Depends(get_db)
) -> ItemResponse:
    """Update an existing item"""
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    update_data = item_update.model_dump(exclude_unset=True)
    if update_data:
        for field, value in update_data.items():
            setattr(item, field, value)
        item.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(item)
    
    logger.info(f"Updated item with id={item_id}")
    return ItemResponse.model_validate(item)


@app.delete(
    "/api/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["items"]
)
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
) -> None:
    """Delete an item"""
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    await db.delete(item)
    await db.commit()
    
    logger.info(f"Deleted item with id={item_id}")


# ============= Test Endpoints =============

@app.get("/api/slow", tags=["testing"])
async def slow_endpoint():
    """Endpoint with artificial delay for async I/O testing"""
    await asyncio.sleep(0.1)
    return {"status": "ok", "delay_ms": 100}


# ============= System Endpoints =============

@app.get("/api/health", response_model=HealthResponse, tags=["system"])
async def health_check() -> HealthResponse:
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        framework="FastAPI",
        version=settings.app_version,
        timestamp=datetime.utcnow()
    )


@app.get("/api/metrics", tags=["system"])
async def get_metrics() -> dict:
    """Simple metrics endpoint"""
    return {
        "framework": "FastAPI",
        "version": settings.app_version,
        "status": "operational"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
