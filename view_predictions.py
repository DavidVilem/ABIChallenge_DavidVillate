from sqlalchemy.orm import Session
from main import SessionLocal, Prediction  

def get_all_predictions():
    db = SessionLocal()
    try:
        predictions = db.query(Prediction).all()
        for pred in predictions:
            print(f"ID: {pred.id}, Model: {pred.model_name}, Input Data: {pred.input_data}, Prediction Result: {pred.prediction_result}")
    finally:
        db.close()

get_all_predictions()