from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import Customer, Order, OrderItem, Product
from ..schemas import OrderCreate, OrderOut

router = APIRouter(prefix="/orders", tags=["orders"])


def _order_with_relations():
    return select(Order).options(selectinload(Order.items), selectinload(Order.customer))


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreate, db: AsyncSession = Depends(get_db)):
    customer = await db.get(Customer, payload.customer_id)
    if customer is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Customer not found")

    # Collapse duplicate product lines so the stock check sees one combined
    # quantity per product rather than validating each line in isolation.
    requested: dict[int, int] = {}
    for item in payload.items:
        requested[item.product_id] = requested.get(item.product_id, 0) + item.quantity

    order = Order(customer_id=customer.id, total_amount=Decimal("0"), status="confirmed")
    total = Decimal("0")

    for product_id, quantity in requested.items():
        # SELECT ... FOR UPDATE locks each product row for the transaction so two
        # concurrent orders cannot both pass the stock check and oversell.
        result = await db.execute(select(Product).where(Product.id == product_id).with_for_update())
        product = result.scalar_one_or_none()
        if product is None:
            await db.rollback()
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Product {product_id} not found")
        if product.quantity < quantity:
            await db.rollback()
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail=f"Insufficient stock for '{product.name}': requested {quantity}, available {product.quantity}",
            )

        subtotal = product.price * quantity
        total += subtotal
        product.quantity -= quantity
        order.items.append(
            OrderItem(
                product_id=product.id,
                product_name=product.name,
                quantity=quantity,
                unit_price=product.price,
                subtotal=subtotal,
            )
        )

    order.total_amount = total
    db.add(order)
    await db.commit()

    result = await db.execute(_order_with_relations().where(Order.id == order.id))
    return result.scalar_one()


@router.get("", response_model=list[OrderOut])
async def list_orders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(_order_with_relations().order_by(Order.id.desc()))
    return result.scalars().all()


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(_order_with_relations().where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(_order_with_relations().where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Order not found")

    # Cancelling an order returns its reserved stock to inventory.
    for item in order.items:
        product = await db.get(Product, item.product_id)
        if product is not None:
            product.quantity += item.quantity

    await db.delete(order)
    await db.commit()
