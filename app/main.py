# Third-party imports
from fastapi import FastAPI, Request
import requests

# Local imports
from predictor import make_prediction

app = FastAPI()

@app.get("/")
def read_root() -> int:
    return {"message": "Excellent!"}


@app.get("/get_ip")
def get_ip():
    '''
    An endpoint to discover the IP address of the API
    '''
    my_ip = requests.get('https://ipinfo.io/ip', verify=False)
    return my_ip


@app.post("/predict")
async def predict(request: Request):
    '''
    Prediction endpoint
    Takes a JSON input and returns a CSV of predictions
    '''
    input_json = await request.json()
    prediction = make_prediction(input_json)
    return prediction


@app.get("/liveness")
def liveness():
    '''
    Liveness endpoint
    Lightweight endpoint to test whether the API is running and processing requests
    '''
    return "API is live"
