# router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import ProductResponse, ProductUpdate, ProductCreate
from typing import List
from crud import (
    create_product as crud_create_product,
    get_products as crud_get_products,
    get_product as crud_get_product,
    delete_product as crud_delete_product,
    update_product as crud_update_product,
)

router = APIRouter()

@router.get("/products/", response_model=List[ProductResponse])
def read_all_products(db: Session = Depends(get_db)):
    return crud_get_products(db)

@router.get("/products/{product_id}", response_model=ProductResponse)  # um item
def read_one_product(product_id: int, db: Session = Depends(get_db)):
    db_product = crud_get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.post("/products/", response_model=ProductResponse)
def create_product_route(product: ProductCreate, db: Session = Depends(get_db)):
    return crud_create_product(db=db, product=product)

@router.delete("/products/{product_id}", response_model=ProductResponse)
def delete_product_route(product_id: int, db: Session = Depends(get_db)):
    deleted = crud_delete_product(db=db, product_id=product_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return deleted

@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product_route(
    product_id: int, product: ProductUpdate, db: Session = Depends(get_db)
):
    db_product = crud_update_product(db, product_id=product_id, product=product)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product
