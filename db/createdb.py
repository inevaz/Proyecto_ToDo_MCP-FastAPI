#creacion de la db 
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship, sessionmaker #declarative base: es una clase base para los modelos de SQLAlchemy, relationship: es una función para definir relaciones entre modelos, sessionmaker: para crear sesiones de base de datos

Base = declarative_base() #base es la clase base para los modelos de SQLAlchemy, que define la estructura de las tablas en la base de datos

class TodoList(Base): #la clase que representa una lista de tareas
    __tablename__ = "todo_list"
    #columnas de la tabla
    id = Column(Integer, primary_key=True, index=True) 
    name = Column(String, nullable=False, unique=True)

    items = relationship("TodoItem", back_populates="todolist")

class TodoItem(Base): #la clase que representa un elemento de una lista de tareas
    __tablename__ = "todo_item"
    #columnas de la tabla
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False, default="Sin descripción")
    completed = Column(Boolean, default=False)
    limit_date = Column(Date, nullable=True)
    todo_list_id = Column(Integer, ForeignKey("todo_list.id"), nullable=False)

    todolist = relationship("TodoList", back_populates="items") #back_populates es una función que define la relación inversa entre los modelos (que si se modifica un modelo, se actualiza el otro automáticamente)

#motor de conexión a SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./todo.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}) #creación de motor de conexión a la base de datos SQLite
#connect_args={"check_same_thread": False} es necesario para que SQLAlchemy funcione correctamente con SQLite en un entorno multihilo (varios hilos de ejecución)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


#lo que ejecuta lo de arriba
if __name__ == "__main__":
    # Crear las tablas
    Base.metadata.create_all(bind=engine) #crea todas las tablas definidas en los modelos
    print("Base de datos creada y tablas generadas.") #just in case