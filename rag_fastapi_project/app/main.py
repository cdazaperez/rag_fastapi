from fastapi import FastAPI, HTTPException
from typing import Dict
from .models import (
    Colegio, ColegioCreate, ColegioUpdate,
    Cliente, ClienteCreate, ClienteUpdate
)

app = FastAPI(title="Gestión de Colegios y Clientes")

# In-memory "database"
colegios: Dict[int, Colegio] = {}
clientes: Dict[int, Cliente] = {}

colegio_id_seq = 1
cliente_id_seq = 1

# Colegio CRUD
@app.post("/colegios", response_model=Colegio)
def create_colegio(colegio: ColegioCreate):
    global colegio_id_seq
    new_colegio = Colegio(id=colegio_id_seq, **colegio.dict())
    colegios[new_colegio.id] = new_colegio
    colegio_id_seq += 1
    return new_colegio

@app.get("/colegios", response_model=list[Colegio])
def list_colegios():
    return list(colegios.values())

@app.get("/colegios/{colegio_id}", response_model=Colegio)
def get_colegio(colegio_id: int):
    colegio = colegios.get(colegio_id)
    if not colegio:
        raise HTTPException(status_code=404, detail="Colegio no encontrado")
    return colegio

@app.put("/colegios/{colegio_id}", response_model=Colegio)
def update_colegio(colegio_id: int, data: ColegioUpdate):
    colegio = colegios.get(colegio_id)
    if not colegio:
        raise HTTPException(status_code=404, detail="Colegio no encontrado")
    updated = colegio.copy(update=data.dict(exclude_unset=True))
    colegios[colegio_id] = updated
    return updated

@app.delete("/colegios/{colegio_id}", status_code=204)
def delete_colegio(colegio_id: int):
    if colegio_id not in colegios:
        raise HTTPException(status_code=404, detail="Colegio no encontrado")
    del colegios[colegio_id]
    return None

# Cliente CRUD
@app.post("/clientes", response_model=Cliente)
def create_cliente(cliente: ClienteCreate):
    global cliente_id_seq
    new_cliente = Cliente(id=cliente_id_seq, **cliente.dict())
    clientes[new_cliente.id] = new_cliente
    cliente_id_seq += 1
    return new_cliente

@app.get("/clientes", response_model=list[Cliente])
def list_clientes():
    return list(clientes.values())

@app.get("/clientes/{cliente_id}", response_model=Cliente)
def get_cliente(cliente_id: int):
    cliente = clientes.get(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@app.put("/clientes/{cliente_id}", response_model=Cliente)
def update_cliente(cliente_id: int, data: ClienteUpdate):
    cliente = clientes.get(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    updated = cliente.copy(update=data.dict(exclude_unset=True))
    clientes[cliente_id] = updated
    return updated

@app.delete("/clientes/{cliente_id}", status_code=204)
def delete_cliente(cliente_id: int):
    if cliente_id not in clientes:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    del clientes[cliente_id]
    return None
