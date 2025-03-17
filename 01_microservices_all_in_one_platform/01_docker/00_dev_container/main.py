from fastapi import FastAPI

app=FastAPI()

@app.get('/')
def read_root():
    return {'message': 'This is root!'}

@app.get('/greetings')
def greeting():
    return {'message': 'hello There, greetings to you!'}