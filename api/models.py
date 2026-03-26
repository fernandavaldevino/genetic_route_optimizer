"""
Modelos Pydantic para a API FastAPI
"""

from typing import List, Optional, Tuple
from pydantic import BaseModel, Field
from enum import Enum


class ServiceType(str, Enum):
    """ Tipos de serviço disponíveis """
    EMERGENCY = "emergency"
    VIOLENCE = "violence"
    MEDICATION = "medication"
    POSTPARTUM = "postpartum"
    REGULAR = "regular"


class ServicePointInput(BaseModel):
    """ Modelo de entrada para ponto de serviço """
    id: int = Field(..., description="ID único do ponto")
    location: Tuple[float, float] = Field(..., description="Coordenadas (x, y)")
    service_type: ServiceType = Field(..., description="Tipo de serviço")
    time_window: Optional[Tuple[float, float]] = Field(None, description="Janela de tempo (início, fim) em minutos")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "location": [100.0, 200.0],
                "service_type": "emergency",
                "time_window": [480, 600]
            }
        }


class OptimizationRequest(BaseModel):
    """ Requisição para otimização de rota """
    service_points: List[ServicePointInput] = Field(..., min_length=1, description="Lista de pontos de serviço")
    num_vehicles: int = Field(1, ge=1, le=2, description="Número de veículos (1 ou 2)")
    population_size: int = Field(100, ge=50, le=500, description="Tamanho da população do algoritmo genético")
    generations: int = Field(200, ge=100, le=1000, description="Número de gerações")
    depot_location: Optional[Tuple[float, float]] = Field(None, description="Localização do depósito")

    class Config:
        json_schema_extra = {
            "example": {
                "service_points": [
                    {
                        "id": 1,
                        "location": [100.0, 200.0],
                        "service_type": "emergency",
                        "time_window": None
                    },
                    {
                        "id": 2,
                        "location": [300.0, 400.0],
                        "service_type": "violence",
                        "time_window": [480, 600]
                    }
                ],
                "num_vehicles": 1,
                "population_size": 100,
                "generations": 200
            }
        }


class StopInfo(BaseModel):
    """ Informações de uma parada """
    id: int
    type: str
    priority: int
    address: str
    coordinates: dict
    time: str
    duration: str
    instructions: str
    special_notes: str


class VehicleRoute(BaseModel):
    """ Rota de um veículo """
    id: int
    driver: str
    total_stops: int
    total_distance: float
    estimated_time: str
    start_time: str
    end_time: str
    stops: List[StopInfo]


class OptimizationResponse(BaseModel):
    """ Resposta da otimização """
    success: bool
    message: str
    date: str
    fitness: float
    num_vehicles: int
    vehicles: List[VehicleRoute]
    execution_time: float

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Otimização concluída com sucesso",
                "date": "2024-01-15T10:30:00",
                "fitness": 0.95,
                "num_vehicles": 1,
                "vehicles": [
                    {
                        "id": 1,
                        "driver": "Motorista 1",
                        "total_stops": 5,
                        "total_distance": 45.5,
                        "estimated_time": "4h 30min",
                        "start_time": "08:00",
                        "end_time": "12:30",
                        "stops": []
                    }
                ],
                "execution_time": 2.5
            }
        }


class RouteListResponse(BaseModel):
    """ Lista de rotas salvas """
    routes: List[dict]
    total: int


class HealthResponse(BaseModel):
    """ Resposta de health check """
    status: str
    version: str
    timestamp: str


class ErrorResponse(BaseModel):
    """ Resposta de erro """
    error: str
    detail: Optional[str] = None
    timestamp: str
