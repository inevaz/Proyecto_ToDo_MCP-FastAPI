from mcp.server.fastmcp import FastMCP
from fastapi import HTTPException
from createdb import SessionLocal, TodoList, TodoItem

mcp = FastMCP()

#recuersos para las listas de tareas
@mcp.resource("file:///todo/lists")
def get_all_lists():
    #devuelve todas las listas desde la db
    with SessionLocal() as db:
        return db.query(TodoList).all()

@mcp.resource("file:///todo/lists/{list_id}")
def get_list(list_id: int):
    #devuelve la lista con id=list_id o tira error
    with SessionLocal() as db:
        lista = db.query(TodoList).filter(TodoList.id == list_id).first()
        if not lista:
            raise HTTPException(status_code=404, detail="Lista no encontrada")
        return lista

#tools para las listas de tareas

@mcp.tool("create_todo_list")
def create_list(name: str):
    #verifico que no exista una lista con el mismo nombre
    with SessionLocal() as db:
        if db.query(TodoList).filter(TodoList.name == name).first():
            raise HTTPException(status_code=400, detail="Ya existe una lista con ese nombre")
        #si no existe, creo una nueva lista con ese nombre y la agrega en la db
        new_list = TodoList(name=name)
        db.add(new_list)
        db.commit()
        db.refresh(new_list)
        return new_list

@mcp.tool("update_todo_list")
def update_list(list_id: int, name: str):
    #busca lista por id y updatea el nombre
    with SessionLocal() as db:
        lista = db.query(TodoList).filter(TodoList.id == list_id).first()
        if not lista:
            raise HTTPException(status_code=404, detail="Lista no encontrada")
        #verifica si el nombre es diferente al actual o si ya existe otra lista con ese nombre
        if getattr(lista, "name", None) != name:
            if db.query(TodoList).filter(TodoList.name == name).first():
                raise HTTPException(status_code=400, detail="Ya existe otra lista con ese nombre") 
        #si no, actualiza el nombre de la lista
        setattr(lista, "name", name)
        db.commit()
        db.refresh(lista)
        return lista

@mcp.tool("delete_todo_list")
def delete_list(list_id: int):
    with SessionLocal() as db:
        lista = db.query(TodoList).filter(TodoList.id == list_id).first()
        if not lista:
            raise HTTPException(status_code=404, detail="Lista no encontrada")
        #borra lista de la db
        db.delete(lista)
        db.commit()
        return {"message": f"Lista {list_id} eliminada correctamente"}

#resources para items que estan en las listas

@mcp.resource("file:///todo/lists/{list_id}/items")
def get_items(list_id: int):
    #si existe la lista con id=list_id, devuelve todos los items de esa lista
    with SessionLocal() as db:
        if not db.query(TodoList).filter(TodoList.id == list_id).first():
            raise HTTPException(status_code=404, detail="Lista no encontrada")
        #return para los items de la lista
        return db.query(TodoItem).filter(TodoItem.todo_list_id == list_id).all()

@mcp.resource("file:///todo/items/{item_id}")
def get_item(item_id: int):
    #busca utem por id y, o devuelve item o tira error
    with SessionLocal() as db:
        item = db.query(TodoItem).filter(TodoItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Ítem no encontrado")
        return item

#tools para items que estan en las listas

@mcp.tool("create_todo_item")
def create_item(list_id: int, description: str, completed: bool = False):
    #verifica si existe o no 
    with SessionLocal() as db:
        if not db.query(TodoList).filter(TodoList.id == list_id).first():
            raise HTTPException(status_code=404, detail="Lista no encontrada")
        #crea un item con los datos y el id de la lista
        new_item = TodoItem(description=description, completed=completed, todo_list_id=list_id)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item

@mcp.tool("update_todo_item")
def update_item(item_id: int, description: str, completed: bool):
    #busco por id
    with SessionLocal() as db:
        item = db.query(TodoItem).filter(TodoItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Ítem no encontrado")
        #actualiza datos del item
        setattr(item, "description", description)
        setattr(item, "completed", completed)
        db.commit()
        db.refresh(item)
        return item

@mcp.tool("delete_todo_item")
def delete_item(item_id: int):
    #busca item por id y borra
    with SessionLocal() as db:
        item = db.query(TodoItem).filter(TodoItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Ítem no encontrado")
        #bora de la db
        db.delete(item)
        db.commit()
        return {"message": f"Ítem {item_id} eliminado correctamente"}

#para que se ejecute el server mcp
if __name__ == "__main__":
    mcp.run()
