from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class ColegioBase(BaseModel):
    nombre: str = Field(..., title="Nombre del colegio")
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    contacto: Optional[str] = None

class ColegioCreate(ColegioBase):
    pass

class ColegioUpdate(ColegioBase):
    pass

class Colegio(ColegioBase):
    id: int

    class Config:
        orm_mode = True

class ClienteBase(BaseModel):
    nombre: str
    apellido: str
    cedula: str = Field(..., title="Número de cédula")
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(ClienteBase):
    pass

class Cliente(ClienteBase):
    id: int

    class Config:
        orm_mode = True
