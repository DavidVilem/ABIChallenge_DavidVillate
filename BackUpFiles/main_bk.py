from fastapi import FastAPI, HTTPException, Request, Form
from pydantic import BaseModel
from typing import List
import pickle
import pandas as pd
import os
import matplotlib.pyplot as plt
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
import json as json_lib  
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
import json
from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI

# Clase para cargar y predecir con modelos desde archivos .pkl
class TitanicModelAPI:
    def __init__(self, model_dir: str):
        """Carga todos los modelos desde los archivos .pkl en el directorio especificado"""
        self.models = {}
        for model_name in os.listdir(model_dir):
            if model_name.endswith(".pkl"):
                model_key = model_name.replace(".pkl", "")
                with open(os.path.join(model_dir, model_name), "rb") as file:
                    self.models[model_key] = pickle.load(file)
        
        # Definir las columnas que el modelo espera
        self.required_columns = ['Pclass', 'Sex', 'Age', 'Fare', 'Embarked', 'Title', 'IsAlone', 'Age_Class']

    def predict(self, model_name: str, data: dict):
        """Realiza una predicción con el modelo especificado"""
        if model_name not in self.models:
            raise ValueError(f"Modelo '{model_name}' no encontrado.")
        
        model = self.models[model_name]

        # Convertir a DataFrame y filtrar solo las columnas necesarias
        input_df = pd.DataFrame([data])
        input_df = input_df[self.required_columns]  # Solo las columnas que el modelo espera

        # Convertir la predicción a int para evitar problemas de tipo
        prediction = int(model.predict(input_df)[0])
        return prediction

# Instancia de FastAPI
app = FastAPI()

# Montar la carpeta Images como contenido estático
app.mount("/images", StaticFiles(directory="Images"), name="images")

# Configuración de plantillas
templates = Jinja2Templates(directory="templates")

# Instancia de TitanicModelAPI con la carpeta que contiene los modelos
titanic_model_api = TitanicModelAPI("Titanic/model_files")

# Endpoint para visualizar el formulario
@app.get("/form")
async def form(request: Request):
    """Renderiza el formulario de entrada para predicción de un solo pasajero"""
    return templates.TemplateResponse("form.html", {"request": request})

# Dependencia para la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/predict_single")
async def predict_single(
    request: Request,
    model_name: str = Form(...),
    Pclass: int = Form(...),
    Sex: int = Form(...),
    Age: int = Form(...),
    Fare: int = Form(...),
    Embarked: int = Form(...),
    Title: int = Form(...),
    IsAlone: int = Form(...),
    Age_Class: int = Form(...),
    db: Session = Depends(get_db)
):
    try:
        passenger_data = {
            "Pclass": Pclass,
            "Sex": Sex,
            "Age": Age,
            "Fare": Fare,
            "Embarked": Embarked,
            "Title": Title,
            "IsAlone": IsAlone,
            "Age_Class": Age_Class
        }
        prediction = titanic_model_api.predict(model_name, passenger_data)
        result = "Sobrevivió" if prediction == 1 else "No sobrevivió"

        # Guardar la predicción en la base de datos
        save_prediction(db, model_name, passenger_data, result)

        return templates.TemplateResponse("form.html", {"request": request, "result": result})
    except Exception as e:
        return templates.TemplateResponse("form.html", {"request": request, "error": str(e)})


# Endpoint para predicciones en lote usando JSON
@app.post("/predict_batch")
async def predict_batch(
    request: Request,
    model_name: str = Form(...),
    json_data: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        passenger_data_list = json_lib.loads(json_data)
        predictions = []

        for passenger_data in passenger_data_list:
            prediction = titanic_model_api.predict(model_name, passenger_data)
            result = "Sobrevivió" if prediction == 1 else "No sobrevivió"
            predictions.append(result)

            # Guardar cada predicción en la base de datos
            save_prediction(db, model_name, passenger_data, result)

        result = f"Predicciones en lote: {predictions}"
        return templates.TemplateResponse("form.html", {"request": request, "result": result})
    except json_lib.JSONDecodeError:
        error_message = "Error en el formato del JSON. Por favor, verifica la sintaxis."
        return templates.TemplateResponse("form.html", {"request": request, "error": error_message})
    except Exception as e:
        error_message = f"Ocurrió un error: {str(e)}"
        return templates.TemplateResponse("form.html", {"request": request, "error": error_message})


# Configuración de la base de datos
DATABASE_URL = "sqlite:///./predictions.db"  # Cambia esta URL si usas otra base de datos
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de tabla para almacenar predicciones
class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, index=True)  # Nombre del modelo usado
    input_data = Column(Text)  # Datos de entrada en formato JSON
    prediction_result = Column(String)  # Resultado de la predicción

# Crear la tabla en la base de datos
Base.metadata.create_all(bind=engine)

def save_prediction(db: Session, model_name: str, input_data: dict, prediction_result: str):
    # Convertir los datos de entrada a JSON para almacenar en la base de datos
    input_data_json = json.dumps(input_data)
    prediction = Prediction(
        model_name=model_name,
        input_data=input_data_json,
        prediction_result=prediction_result
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


# Endpoint para visualizar la gráfica ROC
@app.get("/visualize")
async def visualize_roc():
    """Genera y guarda la gráfica de las curvas ROC para todos los modelos"""
    plt.figure(figsize=(10, 8))
    for model_name, model in titanic_model_api.models.items():
        # Usa el conjunto de prueba X_test_new e y_test_new que creaste en el entrenamiento
        y_proba = model.predict_proba(X_test_new)[:, 1] if hasattr(model, "predict_proba") else model.decision_function(X_test_new)
        fpr, tpr, _ = roc_curve(y_test_new, y_proba)
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, label=f'{model_name} (AUC = {roc_auc:.2f})')

    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Curvas ROC para todos los modelos')
    plt.legend(loc="lower right")
    
    # Guardar la imagen
    plt.savefig("roc_curves.png")
    plt.close()
    
    # Enviar la imagen como respuesta
    return FileResponse("roc_curves.png", media_type="image/png")