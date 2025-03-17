# main.py
from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from app import settings
from sqlmodel import Field, Session, SQLModel, create_engine, select, Sequence
from fastapi import FastAPI, Depends
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer,AIOKafkaConsumer
import json


class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(index=True)

class Order(SQLModel):
    id: Optional[int] = Field(default=None)
    username: str
    product_id: int
    product_name: str
    product_price: int

# https://fastapi.tiangolo.com/advanced/events/#lifespan-function
@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Initiating product service...")
    # create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1",
    servers=[
        {
            "url": "http://127.0.0.1:8000", 
            "description": "Development Server"
        }
        ])

# def get_session():
#     with Session(engine) as session:
#         yield session


@app.get("/")
def read_root():
    return {"Message": "product service"}

@app.post("/create_order")
async def create_order(order: Order):
    producer= AIOKafkaProducer(bootstrap_servers="broker:19092")
    await producer.start()
    orderJSON= json.dumps(order.__dict__).encode('utf-8')

    print({"orderJson":orderJSON})
    try:
        await producer.send_and_wait("order", orderJSON)
    finally:
        await producer.stop()
    return {"message": "successful!"}
    # return {
    #     "id": 1,
    #     "username": "harry",
    #     "product_id": 1,
    #     "product_name": "first_product",
    #     "product_price": 200
    # } 

@app.get("/read_order")
async def read_order():
    consumer= AIOKafkaConsumer(
        'order',
        bootstrap_servers="broker:19092",
        group_id="order_consumer"
    )
    await consumer.start()

    try:
        async for msg in consumer:
            print("consumed: ", msg.topic, msg.partition, msg.offset,
                  msg.key, msg.value, msg.timestamp)
    finally:
        await consumer.stop()
    return {"message": consumer}