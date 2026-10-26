import re
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, ValidationInfo, field_validator


DDDS_VALIDOS = {
    "11", "12", "13", "14", "15", "16", "17", "18", "19",
    "21", "22", "24", "27", "28",
    "31", "32", "33", "34", "35", "37", "38",
    "41", "42", "43", "44", "45", "46", "47", "48", "49",
    "51", "53", "54", "55",
    "61", "62", "63", "64", "65", "66", "67", "68", "69",
    "71", "73", "74", "75", "77", "79",
    "81", "82", "83", "84", "85", "86", "87", "88", "89",
    "91", "92", "93", "94", "95", "96", "97", "98", "99",
}

REGEX_EMAIL = re.compile(
    r"^[a-z0-9]+([._%+-][a-z0-9]+)*"
    r"@"
    r"([a-z0-9]([a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,}$"
)


def _texto_obrigatorio(minimo: int, maximo: int) -> BeforeValidator:
    def validar(valor, info: ValidationInfo):
        campo = info.field_name
        if valor is None:
            raise ValueError(f"O campo '{campo}' não pode ser nulo.")
        if not isinstance(valor, str):
            return valor
        valor = valor.strip()
        if not valor:
            raise ValueError(f"O campo '{campo}' não pode ficar vazio nem conter apenas espaços.")
        if len(valor) < minimo:
            raise ValueError(f"O campo '{campo}' deve ter no mínimo {minimo} caracteres.")
        if len(valor) > maximo:
            raise ValueError(f"O campo '{campo}' deve ter no máximo {maximo} caracteres.")
        return valor

    return BeforeValidator(validar)


def _texto_opcional(maximo: int) -> BeforeValidator:
    return _texto_obrigatorio(1, maximo)


def _validar_email(valor, info: ValidationInfo):
    if valor is None:
        raise ValueError("O campo 'email' não pode ser nulo.")
    if not isinstance(valor, str):
        return valor
    valor = valor.strip().lower()
    if not valor:
        raise ValueError("O campo 'email' não pode ficar vazio nem conter apenas espaços.")
    if len(valor) > 150:
        raise ValueError("O campo 'email' deve ter no máximo 150 caracteres.")
    if not REGEX_EMAIL.match(valor) or len(valor.split("@")[0]) > 64:
        raise ValueError("E-mail inválido. Use o formato nome@dominio.com.")
    return valor


def _validar_telefone(valor, info: ValidationInfo):
    if valor is None:
        raise ValueError("O campo 'telefone' não pode ser nulo.")
    if not isinstance(valor, str):
        return valor
    valor = valor.strip()
    if not valor:
        raise ValueError("O campo 'telefone' não pode ficar vazio nem conter apenas espaços.")

    digitos = re.sub(r"[\s()\-]", "", valor)
    if not digitos.isdigit():
        raise ValueError("Telefone inválido. Use apenas números, por exemplo: 11999998888.")
    if len(digitos) != 11:
        raise ValueError("Telefone inválido. Informe o DDD + número com 11 dígitos, por exemplo: 11999998888.")
    if digitos[:2] not in DDDS_VALIDOS:
        raise ValueError(f"Telefone inválido. O DDD {digitos[:2]} não existe.")
    if digitos[2] != "9":
        raise ValueError("Telefone inválido. O número de celular deve começar com 9 depois do DDD.")
    if len(set(digitos[2:])) == 1:
        raise ValueError("Telefone inválido. O número não pode ter todos os dígitos repetidos.")
    return digitos


Nome = Annotated[str, _texto_obrigatorio(2, 100)]
Email = Annotated[str, BeforeValidator(_validar_email)]
Telefone = Annotated[str, BeforeValidator(_validar_telefone)]
UsuarioResponsavel = Annotated[str, _texto_obrigatorio(2, 100)]


class TipoPessoaResponseSchema(BaseModel):
    id: int
    descricao: str

    model_config = ConfigDict(from_attributes=True)


def _validar_tipo_pessoa_id(valor: int) -> int:
    if valor not in (1, 2):
        raise ValueError("Tipo de pessoa inválido. Use 1 para ALUNO ou 2 para PERSONAL.")
    return valor


class PessoaBase(BaseModel):
    nome: Nome
    email: Email
    telefone: Telefone
    tipo_pessoa_id: int

    @field_validator("tipo_pessoa_id")
    @classmethod
    def validar_tipo_pessoa_id(cls, valor: int) -> int:
        return _validar_tipo_pessoa_id(valor)


class PessoaCreateSchema(PessoaBase):
    pass


class PessoaUpdateSchema(BaseModel):
    nome: Nome = None
    email: Email = None
    telefone: Telefone = None
    tipo_pessoa_id: int = None

    @field_validator("tipo_pessoa_id")
    @classmethod
    def validar_tipo_pessoa_id(cls, valor: int) -> int:
        return _validar_tipo_pessoa_id(valor)


class PessoaResponseSchema(BaseModel):
    matricula: int
    nome: str
    email: str
    telefone: str
    tipo_pessoa_id: int
    data_criacao: datetime
    tipo: TipoPessoaResponseSchema

    model_config = ConfigDict(from_attributes=True)


class PessoaResumoSchema(BaseModel):
    matricula: int
    nome: str
    tipo_pessoa_id: int

    model_config = ConfigDict(from_attributes=True)


class MatriculaAlunoCreateSchema(BaseModel):
    aluno_matricula: int = Field(gt=0)
    personal_matricula: int = Field(gt=0)
    usuario_inclusao: UsuarioResponsavel


class MatriculaAlunoUpdateSchema(BaseModel):
    personal_matricula: int = Field(gt=0)
    usuario_alteracao: UsuarioResponsavel


class MatriculaAlunoResponseSchema(BaseModel):
    id: int
    aluno: PessoaResumoSchema
    personal: PessoaResumoSchema
    usuario_inclusao: str
    data_inclusao: datetime
    usuario_alteracao: str | None
    data_alteracao: datetime | None

    model_config = ConfigDict(from_attributes=True)


class TreinoBaseSchema(BaseModel):
    nome: Nome
    descricao: Annotated[str, _texto_opcional(1000)] = None
    objetivo: Annotated[str, _texto_opcional(150)] = None
    nivel: Annotated[str, _texto_opcional(30)] = None


class TreinoCreateSchema(TreinoBaseSchema):
    pass


class TreinoUpdateSchema(BaseModel):
    nome: Nome = None
    descricao: Annotated[str, _texto_opcional(1000)] = None
    objetivo: Annotated[str, _texto_opcional(150)] = None
    nivel: Annotated[str, _texto_opcional(30)] = None


class TreinoResponseSchema(BaseModel):
    id: int
    nome: str
    descricao: str | None
    objetivo: str | None
    nivel: str | None
    data_criacao: datetime

    model_config = ConfigDict(from_attributes=True)


class FichaTreinoCreateSchema(BaseModel):
    aluno_matricula: int = Field(gt=0)
    personal_matricula: int = Field(gt=0)
    treino_id: int = Field(gt=0)
    observacoes: Annotated[str, _texto_opcional(1500)] = None


class FichaTreinoUpdateSchema(BaseModel):
    personal_matricula: int = Field(default=None, gt=0)
    treino_id: int = Field(default=None, gt=0)
    observacoes: Annotated[str, _texto_opcional(1500)] = None


class FichaTreinoResponseSchema(BaseModel):
    id: int
    aluno: PessoaResumoSchema
    personal: PessoaResumoSchema
    treino: TreinoResponseSchema
    observacoes: str | None
    data_criacao: datetime

    model_config = ConfigDict(from_attributes=True)
