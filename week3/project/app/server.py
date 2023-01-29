from fastapi import FastAPI
from pydantic import BaseModel
from loguru import logger

from classifier import NewsCategoryClassifier
from datetime import datetime


class PredictRequest(BaseModel):
    source: str
    url: str
    title: str
    description: str


class PredictResponse(BaseModel):
    scores: dict
    label: str


MODEL_PATH = "../data/news_classifier.joblib"
LOGS_OUTPUT_PATH = "../data/logs.out"

app = FastAPI()


@app.on_event("startup")
def startup_event():
    """
    [TO BE IMPLEMENTED]
    1. Initialize an instance of `NewsCategoryClassifier`.
    2. Load the serialized trained model parameters (pointed to by `MODEL_PATH`) into the NewsCategoryClassifier you initialized.
    3. Open an output file to write logs, at the destimation specififed by `LOGS_OUTPUT_PATH`
        
    Access to the model instance and log file will be needed in /predict endpoint, make sure you
    store them as global variables
    """
    global news_classifier
    news_classifier = NewsCategoryClassifier(verbose=True)
    news_classifier.load(MODEL_PATH)
    global loggs_file
    loggs_file = open(file=LOGS_OUTPUT_PATH, mode="a")
    logger.info("Setup completed")


@app.on_event("shutdown")
def shutdown_event():
    # clean up
    """
    [TO BE IMPLEMENTED]
    1. Make sure to flush the log file and close any file pointers to avoid corruption
    2. Any other cleanups
    """
    logger.info("Shutting down application")
    with open(LOGS_OUTPUT_PATH, "w+") as file:
        file.flush()
        file.close()


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    # get model prediction for the input request
    # construct the data to be logged
    # construct response
    """
    [TO BE IMPLEMENTED]
    1. run model inference and get model predictions for model inputs specified in `request`
    2. Log the following data to the log file (the data should be logged to the file that was opened in `startup_event`)
    {
        'timestamp': <YYYY:MM:DD HH:MM:SS> format, when the request was received,
        'request': dictionary representation of the input request,
        'prediction': dictionary representation of the response,
        'latency': time it took to serve the request, in millisec
    }
    3. Construct an instance of `PredictResponse` and return
    """
    start_time = datetime.now()
    if news_classifier == None:
        startup_event()
    
    preds = news_classifier.predict_proba(request.dict())
    label = sorted(preds.items(), key=lambda x: x[1], reverse=True)[0][0]
    response = PredictResponse(scores=preds.items(), label=label)

    end_time = datetime.now()

    loggs = dict(
        timestamp=datetime.now().strftime("%Y:%m:%d %H:%M:%S"),
        request=request.dict(),
        prediction=response.dict(),
        latency=end_time - start_time
        )
    loggs_file.write(str(loggs) + "\n")
    loggs_file.flush()

    return response


@app.get("/")
def read_root():
    return {"Hello": "World"}
