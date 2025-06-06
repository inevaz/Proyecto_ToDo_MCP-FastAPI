from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List as TypeList, Optional
from datetime import date
from pydantic import BaseModel
from createdb import SessionLocal, TodoList, TodoItem  # Modelos y base de datos creados en otro archivo

app = FastAPI()

#primero abro sesión a la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#esquemas de Pydantic para validación de datos
#estos esquemas se usan para validar, serializar y definir los datos de entrada y salida de la API
#Es mejor usar Pydantic para definir los esquemas de datos sobre todo porque valida mejor los datos y es mas facil con fastapi
class TodoItemSchema(BaseModel): #modelo de entrada para los items de las listas
    description: str
    completed: bool = False
    limit_date: Optional[date] = None

class TodoItemResponseSchema(TodoItemSchema): #modelo de salida para los items de las listas
    id: int
    todo_list_id: int

    class Config: #configuracion para Pydantic
        from_attributes = True  #permite convertir modelos SQLAlchemy a Pydantic

class TodoListSchema(BaseModel): #modelo de entrada para las listas de tareas
    name: str

class TodoListResponseSchema(TodoListSchema): #modelo de salida para las listas de tareas
    id: int
    items: TypeList[TodoItemResponseSchema] = [] #lista de items de la lista de tareas

    class Config: #configuracion para Pydantic
        from_attributes = True 

#endpoints para las listas de tareas
@app.get("/lists", response_model=TypeList[TodoListResponseSchema]) #get de todas las listas
def get_lists(db: Session = Depends(get_db)): #devuelve todas las listas de tareas
    return db.query(TodoList).all() #devuelve todas las listas

@app.post("/lists", response_model=TodoListResponseSchema) #post para crear una lista
def create_list(list_data: TodoListSchema, db: Session = Depends(get_db)): #crea una nueva lista
    if db.query(TodoList).filter(TodoList.name == list_data.name).first(): #verifica si ya existe una lista con el mismo nombre
        raise HTTPException(status_code=400, detail="Ya existe una lista con ese nombre") #si hay, tira un error
    new_list = TodoList(name=list_data.name) #si no, crea una nueva lista con el nombre
    db.add(new_list) #agrega la nueva lista a la sesión de la base de datos
    db.commit() #confirma los cambios en la base de datos
    db.refresh(new_list) #actualiza el objeto new_list con los datos de la base de datos
    return new_list #devuelve la nueva lista creada

@app.get("/lists/{list_id}", response_model=TodoListResponseSchema) #get de una lista en particular
def get_list(list_id: int, db: Session = Depends(get_db)): #devuelve una lista por su id
    lista = db.query(TodoList).filter(TodoList.id == list_id).first() #busca la lista por su id
    if not lista: #si no encuentra la lista, tira un error
        raise HTTPException(status_code=404, detail="Lista no encontrada") #si no encuentra la lista, tira un error
    return lista #devuelve la lista encontrada

@app.put("/lists/{list_id}", response_model=TodoListResponseSchema) #put para actualizar una lista
def update_list(list_id: int, list_data: TodoListSchema, db: Session = Depends(get_db)): #actualiza una lista por su id
    lista = db.query(TodoList).filter(TodoList.id == list_id).first() #busca la lista por su id
    if not lista: #si no encuentra la lista, tira un error
        raise HTTPException(status_code=404, detail="Lista no encontrada") 
    if getattr(lista, "name", None) != list_data.name: #si el nombre de la lista es diferente al de la lista que se quiere actualizar
        if db.query(TodoList).filter(TodoList.name == list_data.name).first(): #verifica si ya existe una lista con el mismo nombre
            raise HTTPException(status_code=400, detail="Ya existe otra lista con ese nombre") #si hay, tira un error
    setattr(lista, "name", list_data.name) #actualiza el nombre de la lista
    db.commit() #confirma los cambios en la base de datos
    db.refresh(lista) #actualiza el objeto lista con los datos de la base de datos
    return lista #devuelve la lista actualizada

@app.delete("/lists/{list_id}") #delete para eliminar una lista
def delete_list(list_id: int, db: Session = Depends(get_db)): #elimina una lista por su id
    lista = db.query(TodoList).filter(TodoList.id == list_id).first() #busca la lista por su id
    if not lista:
        raise HTTPException(status_code=404, detail="Lista no encontrada") #si no encuentra la lista, tira un error
    db.delete(lista) #elimina la lista de la sesión de la base de datos
    db.commit() #confirma los cambios en la base de datos
    return {"message": f"Lista {list_id} eliminada correctamente"} #msj de confrimacion


#endpoints para items que estan en las listas
@app.get("/lists/{list_id}/items", response_model=TypeList[TodoItemResponseSchema]) #get de los items de una lista
def get_items(list_id: int, db: Session = Depends(get_db)): #devuelve todos los items de una lista por su id
    if not db.query(TodoList).filter(TodoList.id == list_id).first(): #verifica si la lista existe
        raise HTTPException(status_code=404, detail="Lista no encontrada") #si no existe, tira un error
    return db.query(TodoItem).filter(TodoItem.todo_list_id == list_id).all() #devuelve todos los items de la lista

@app.post("/lists/{list_id}/items", response_model=TodoItemResponseSchema) #post para crear un item en una lista
def create_item(list_id: int, item_data: TodoItemSchema, db: Session = Depends(get_db)): #crea un nuevo item en una lista por su id
    if not db.query(TodoList).filter(TodoList.id == list_id).first(): #verifica si la lista existe
        raise HTTPException(status_code=404, detail="Lista no encontrada")  #si no existe, tira un error
    new_item = TodoItem(**item_data.model_dump(), todo_list_id=list_id) #crea un nuevo item con los datos del item y el id de la lista
    db.add(new_item) #agrega el nuevo item a la sesión de la base de datos
    db.commit() #confirma los cambios en la base de datos
    db.refresh(new_item) #actualiza el objeto new_item con los datos de la base de datos
    return new_item #devuelve el nuevo item creado

@app.put("/items/{item_id}", response_model=TodoItemResponseSchema) #put para actualizar un item
def update_item(item_id: int, item_data: TodoItemSchema, db: Session = Depends(get_db)): #actualiza un item por su id
    item = db.query(TodoItem).filter(TodoItem.id == item_id).first() #busca el item por su id
    if not item:  #si no encuentra el item, tira un error
        raise HTTPException(status_code=404, detail="Ítem no encontrado") 
    for key, value in item_data.model_dump().items(): #recorre los datos del item a actualizar
        setattr(item, key, value) #actualiza los datos del item
    db.commit() #confirma los cambios en la base de datos
    db.refresh(item) #actualiza el objeto item con los datos de la base de datos
    return item #devuelve el item actualizado

@app.delete("/items/{item_id}") #delete para eliminar un item
def delete_item(item_id: int, db: Session = Depends(get_db)): #elimina un item por su id
    item = db.query(TodoItem).filter(TodoItem.id == item_id).first() #busca el item por su id
    if not item:  #si no encuentra el item, tira un error
        raise HTTPException(status_code=404, detail="Ítem no encontrado") 
    db.delete(item) #elimina el item de la sesión de la base de datos
    db.commit() #confirma los cambios en la base de datos
    return {"message": f"Ítem {item_id} eliminado correctamente"}

#indico la ruta de la API
@app.get("/")
def root():
    return {
        "message": "conectado a la API de Todo List",
    }
