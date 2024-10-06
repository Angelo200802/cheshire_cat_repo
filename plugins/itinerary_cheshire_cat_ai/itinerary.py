from pydantic import BaseModel, ValidationError,Field, field_validator, model_validator
import re
from datetime import datetime
from typing import Optional

class Itinerary(BaseModel):
    country : str = Field(description="Città in cui si vorrebbe andare",pattern=r'^[a-zA-Z\s]+$')
    start_date : str = Field(description="Data inizio itinerario",pattern = r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$')
    finish_date : str = Field(description="Data di fine dell'itinerario", pattern = r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$')
    budget : float = Field(description="Budget di spesa per l'itinearario",ge=0)
    description : str = Field(description="Descrizione delle attività dell'itinerario")

    @model_validator(mode='before')
    def check_dates(cls, values):
        start_date = values.get('start_date')
        finish_date = values.get('finish_date')
        if start_date is not None:
            date1 = datetime.strptime(start_date, "%d/%m/%Y").date()
            if date1 < datetime.now().date():
                raise ValueError("L'itinerario non può partire da un giorno precedente ad oggi")
            if finish_date is not None:
                date2 = datetime.strptime(finish_date, "%d/%m/%Y").date()
                if date1 > date2:
                    raise ValueError("La data di inizio non può essere successiva alla data di fine")
        return values
    