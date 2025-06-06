FROM python:3.13-slim

WORKDIR /app

#copio archivos necesarios
COPY db/ ./
COPY requirements.txt .

#instala dependencias
RUN pip install -r requirements.txt

#runnea para que se cree la db
RUN python createdb.py

#ejecuta servidor
CMD ["python", "todo_mcp.py"]
