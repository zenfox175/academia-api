from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import relationship

from database import Base


class TipoPessoa(Base):
    __tablename__ = "tipos_pessoa"

    id = Column(Integer, primary_key=True)
    descricao = Column(String(20), nullable=False, unique=True)

    pessoas = relationship("Pessoa", back_populates="tipo")


class Pessoa(Base):
    __tablename__ = "pessoas"

    matricula = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nome = Column(String(100), nullable=False, index=True)
    email = Column(String(150), nullable=False, unique=True, index=True)
    telefone = Column(String(11), nullable=False, unique=True, index=True)
    tipo_pessoa_id = Column(Integer, ForeignKey("tipos_pessoa.id"), nullable=False, index=True)
    data_criacao = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    tipo = relationship("TipoPessoa", back_populates="pessoas")
    matricula_como_aluno = relationship(
        "MatriculaAluno",
        foreign_keys="MatriculaAluno.aluno_matricula",
        back_populates="aluno",
        uselist=False,
    )
    alunos_atendidos = relationship(
        "MatriculaAluno",
        foreign_keys="MatriculaAluno.personal_matricula",
        back_populates="personal",
    )
    fichas_como_aluno = relationship(
        "FichaTreino",
        foreign_keys="FichaTreino.aluno_matricula",
        back_populates="aluno",
    )
    fichas_como_personal = relationship(
        "FichaTreino",
        foreign_keys="FichaTreino.personal_matricula",
        back_populates="personal",
    )


class MatriculaAluno(Base):
    __tablename__ = "matriculas_alunos"

    id = Column(Integer, primary_key=True, index=True)
    aluno_matricula = Column(
        Integer,
        ForeignKey("pessoas.matricula", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    personal_matricula = Column(
        Integer,
        ForeignKey("pessoas.matricula"),
        nullable=False,
        index=True,
    )
    usuario_inclusao = Column(String(100), nullable=False)
    data_inclusao = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    usuario_alteracao = Column(String(100), nullable=True)
    data_alteracao = Column(DateTime, nullable=True, onupdate=func.current_timestamp())

    aluno = relationship(
        "Pessoa",
        foreign_keys=[aluno_matricula],
        back_populates="matricula_como_aluno",
    )
    personal = relationship(
        "Pessoa",
        foreign_keys=[personal_matricula],
        back_populates="alunos_atendidos",
    )


class Treino(Base):
    __tablename__ = "treinos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, index=True)
    descricao = Column(Text, nullable=True)
    objetivo = Column(String(150), nullable=True)
    nivel = Column(String(30), nullable=True)
    data_criacao = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    fichas = relationship("FichaTreino", back_populates="treino", cascade="all, delete-orphan")


class FichaTreino(Base):
    __tablename__ = "fichas_treino"
    __table_args__ = (
        UniqueConstraint("aluno_matricula", "treino_id", name="uq_ficha_aluno_treino"),
    )

    id = Column(Integer, primary_key=True, index=True)
    aluno_matricula = Column(
        Integer,
        ForeignKey("pessoas.matricula", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    personal_matricula = Column(
        Integer,
        ForeignKey("pessoas.matricula"),
        nullable=False,
        index=True,
    )
    treino_id = Column(Integer, ForeignKey("treinos.id", ondelete="CASCADE"), nullable=False, index=True)
    observacoes = Column(Text, nullable=True)
    data_criacao = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    aluno = relationship("Pessoa", foreign_keys=[aluno_matricula], back_populates="fichas_como_aluno")
    personal = relationship("Pessoa", foreign_keys=[personal_matricula], back_populates="fichas_como_personal")
    treino = relationship("Treino", back_populates="fichas")
