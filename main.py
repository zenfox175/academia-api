from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import models
from database import Base, SessionLocal, engine
from routers import fichas_treino, matriculas, pessoas, tipos_pessoa, treinos


Base.metadata.create_all(bind=engine)


def criar_tipos_pessoa_padrao():
    db = SessionLocal()
    try:
        tipos = [
            (1, "ALUNO"),
            (2, "PERSONAL"),
        ]
        for tipo_id, descricao in tipos:
            existe = db.query(models.TipoPessoa).filter(models.TipoPessoa.id == tipo_id).first()
            if not existe:
                db.add(models.TipoPessoa(id=tipo_id, descricao=descricao))
        db.commit()
    finally:
        db.close()


criar_tipos_pessoa_padrao()

app = FastAPI(
    title="Academia FitTec",
    description=(
        "API da Academia FitTec para gerenciamento de alunos, personal trainers, "
        "matrículas, treinos e fichas de treino."
    ),
    version="3.0.0",
)

app.include_router(pessoas.router)
app.include_router(tipos_pessoa.router)
app.include_router(matriculas.router)
app.include_router(treinos.router)
app.include_router(fichas_treino.router)


def _mensagem_erro(erro: dict) -> str:
    tipo = erro.get("type", "")
    ctx = erro.get("ctx") or {}

    if tipo == "missing":
        return "Campo obrigatório."
    if tipo in ("string_type", "int_type", "int_parsing") and erro.get("input") is None:
        return "Este campo não pode ser nulo."
    if tipo == "string_type":
        return "Deve ser um texto."
    if tipo in ("int_type", "int_parsing"):
        return "Deve ser um número inteiro."
    if tipo == "greater_than":
        return f"Deve ser maior que {ctx.get('gt')}."
    if tipo == "json_invalid":
        return "O JSON enviado é inválido."
    if tipo == "value_error":
        return erro.get("msg", "").removeprefix("Value error, ")
    return erro.get("msg", "Valor inválido.")


@app.exception_handler(RequestValidationError)
def tratar_erro_validacao(request: Request, exc: RequestValidationError):
    erros = []
    for erro in exc.errors():
        local = [str(parte) for parte in erro.get("loc", ()) if parte not in ("body", "query", "path")]
        campo = ".".join(local) if erro.get("type") != "json_invalid" and local else "corpo da requisição"
        erros.append({"campo": campo, "mensagem": _mensagem_erro(erro)})

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Dados inválidos. Corrija os campos abaixo e tente novamente.",
            "erros": erros,
        },
    )


@app.get("/", tags=["Início"])
def inicio():
    return {"status": "API Academia FitTec funcionando!"}
