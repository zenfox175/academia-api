from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

import models
import schemas
from database import get_db


router = APIRouter(prefix="/pessoas", tags=["Pessoas"])


def _buscar_pessoa_ou_404(matricula: int, db: Session) -> models.Pessoa:
    pessoa = (
        db.query(models.Pessoa)
        .options(joinedload(models.Pessoa.tipo))
        .filter(models.Pessoa.matricula == matricula)
        .first()
    )
    if not pessoa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pessoa não encontrada.",
        )
    return pessoa


def _salvar_ou_409(db: Session, mensagem: str) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=mensagem,
        )


def _garantir_email_e_telefone_unicos(
    db: Session,
    email: str | None = None,
    telefone: str | None = None,
    ignorar_matricula: int | None = None,
) -> None:
    if email is not None:
        query = db.query(models.Pessoa).filter(func.lower(models.Pessoa.email) == email.lower())
        if ignorar_matricula is not None:
            query = query.filter(models.Pessoa.matricula != ignorar_matricula)
        if query.first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="E-mail já cadastrado para outra pessoa.",
            )

    if telefone is not None:
        query = db.query(models.Pessoa).filter(models.Pessoa.telefone == telefone)
        if ignorar_matricula is not None:
            query = query.filter(models.Pessoa.matricula != ignorar_matricula)
        if query.first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Telefone já cadastrado para outra pessoa.",
            )


def _validar_tipo_pessoa(tipo_pessoa_id: int, db: Session) -> None:
    tipo = db.query(models.TipoPessoa).filter(models.TipoPessoa.id == tipo_pessoa_id).first()
    if not tipo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de pessoa inválido. Use 1 para ALUNO ou 2 para PERSONAL.",
        )


@router.get("/", response_model=List[schemas.PessoaResponseSchema])
def listar_pessoas(
    matricula: int | None = None,
    nome: str | None = None,
    email: str | None = None,
    telefone: str | None = None,
    tipo_pessoa_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Pessoa).options(joinedload(models.Pessoa.tipo))

    if matricula:
        query = query.filter(models.Pessoa.matricula == matricula)
    if nome:
        query = query.filter(models.Pessoa.nome.ilike(f"%{nome}%"))
    if email:
        query = query.filter(models.Pessoa.email.ilike(f"%{email}%"))
    if telefone:
        query = query.filter(models.Pessoa.telefone.ilike(f"%{telefone}%"))
    if tipo_pessoa_id:
        query = query.filter(models.Pessoa.tipo_pessoa_id == tipo_pessoa_id)

    return query.order_by(models.Pessoa.nome).all()


@router.get("/{matricula}", response_model=schemas.PessoaResponseSchema)
def buscar_pessoa(matricula: int, db: Session = Depends(get_db)):
    return _buscar_pessoa_ou_404(matricula, db)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.PessoaResponseSchema,
)
def cadastrar_pessoa(
    pessoa: schemas.PessoaCreateSchema,
    db: Session = Depends(get_db),
):
    _validar_tipo_pessoa(pessoa.tipo_pessoa_id, db)
    _garantir_email_e_telefone_unicos(db, pessoa.email, pessoa.telefone)
    nova_pessoa = models.Pessoa(**pessoa.model_dump())
    db.add(nova_pessoa)
    _salvar_ou_409(db, "E-mail ou telefone já cadastrado para outra pessoa.")
    return _buscar_pessoa_ou_404(nova_pessoa.matricula, db)


@router.put("/{matricula}", response_model=schemas.PessoaResponseSchema)
def atualizar_pessoa(
    matricula: int,
    dados: schemas.PessoaUpdateSchema,
    db: Session = Depends(get_db),
):
    pessoa = _buscar_pessoa_ou_404(matricula, db)
    alteracoes = dados.model_dump(exclude_unset=True)

    if "tipo_pessoa_id" in alteracoes:
        _validar_tipo_pessoa(alteracoes["tipo_pessoa_id"], db)

    _garantir_email_e_telefone_unicos(
        db,
        email=alteracoes.get("email"),
        telefone=alteracoes.get("telefone"),
        ignorar_matricula=matricula,
    )

    for campo, valor in alteracoes.items():
        setattr(pessoa, campo, valor)

    _salvar_ou_409(db, "E-mail ou telefone já cadastrado para outra pessoa.")
    return _buscar_pessoa_ou_404(matricula, db)


@router.delete("/{matricula}")
def excluir_pessoa(matricula: int, db: Session = Depends(get_db)):
    pessoa = _buscar_pessoa_ou_404(matricula, db)

    possui_matricula = (
        db.query(models.MatriculaAluno)
        .filter(
            (models.MatriculaAluno.aluno_matricula == matricula)
            | (models.MatriculaAluno.personal_matricula == matricula)
        )
        .first()
    )
    possui_ficha = (
        db.query(models.FichaTreino)
        .filter(
            (models.FichaTreino.aluno_matricula == matricula)
            | (models.FichaTreino.personal_matricula == matricula)
        )
        .first()
    )
    if possui_matricula or possui_ficha:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A pessoa possui vínculos cadastrados e não pode ser removida.",
        )

    db.delete(pessoa)
    db.commit()
    return {"mensagem": "Pessoa removida com sucesso."}
