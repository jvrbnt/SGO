from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"MiNa_SGO": "Entorno Verificado"}