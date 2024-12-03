from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import pickle
from datetime import datetime, timedelta
import json

# Initialize FastAPI app
app = FastAPI()

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Load the saved model
with open("commodity_price_model.pkl", "rb") as file:
    model = pickle.load(file)


# Home page (GET method)
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Prediction endpoint (POST method)
@app.post("/predict", response_class=HTMLResponse)
async def predict(request: Request, start_date: str = Form(...)):
    # Parse user-provided date
    start_date = datetime.strptime(start_date, "%Y-%m-%d")

    # Generate future dates (next 120 days)
    future_dates = pd.date_range(start=start_date, periods=120).to_frame(index=False, name="ds")

    # Predict using the model
    forecast = model.predict(future_dates)

    # Prepare data for the graph
    graph_data = {
        "dates": forecast["ds"].dt.strftime("%Y-%m-%d").tolist(),
        "prices": forecast["yhat"].tolist()
    }

    # Return updated template with prediction data
    return templates.TemplateResponse("index.html", {"request": request, "graph_data": json.dumps(graph_data)})