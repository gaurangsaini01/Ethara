from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..database import get_db
from ..models import Customer, Order, Product
from ..schemas import DashboardOut

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOut)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    threshold = get_settings().low_stock_threshold

    total_products = await db.scalar(select(func.count()).select_from(Product))
    total_customers = await db.scalar(select(func.count()).select_from(Customer))
    total_orders = await db.scalar(select(func.count()).select_from(Order))

    low_stock = (
        await db.execute(select(Product).where(Product.quantity <= threshold).order_by(Product.quantity))
    ).scalars().all()

    return DashboardOut(
        total_products=total_products or 0,
        total_customers=total_customers or 0,
        total_orders=total_orders or 0,
        low_stock_count=len(low_stock),
        low_stock_products=list(low_stock),
    )
