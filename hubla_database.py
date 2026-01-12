from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    create_engine,
    String,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    select,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)


# -------------------------
# Base / Engine / Session
# -------------------------
class Base(DeclarativeBase):
    pass


def make_engine(sqlite_path: str = "hubla_database.sqlite"):
    return create_engine(f"sqlite:///{sqlite_path}", future=True)


def make_session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db(engine):
    Base.metadata.create_all(engine)


# -------------------------
# Helpers
# -------------------------
def parse_created_at(iso_z: str) -> datetime:
    # Ex: "2025-12-20T20:57:55.000Z"
    return datetime.fromisoformat(iso_z.replace("Z", "+00:00"))


# -------------------------
# Models (SIMPLIFICADOS)
# -------------------------
class Produto(Base):
    __tablename__ = "produtos"

    # ID do produto = offer_id
    offer_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    vendas: Mapped[List["Venda"]] = relationship(back_populates="produto")


class Cliente(Base):
    __tablename__ = "clientes"

    # ID do cliente = payer_id
    payer_id: Mapped[str] = mapped_column(String(64), primary_key=True)

    cnpj: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    nome: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    vendas: Mapped[List["Venda"]] = relationship(back_populates="cliente")


class Venda(Base):
    __tablename__ = "vendas"

    # ID do lançamento = sale['id']
    sale_id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Vínculos
    payer_id: Mapped[str] = mapped_column(ForeignKey("clientes.payer_id"), nullable=False, index=True)
    offer_id: Mapped[str] = mapped_column(ForeignKey("produtos.offer_id"), nullable=False, index=True)

    # Campos do lançamento
    installment_fee_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    payment_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    price_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    product_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    # JSON bruto da sale
    raw_json: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    cliente: Mapped[Cliente] = relationship(back_populates="vendas")
    produto: Mapped[Produto] = relationship(back_populates="vendas")


# -------------------------
# Upserts
# -------------------------
def upsert_offers(session, offers: List[Dict[str, Any]]) -> int:
    """
    Cadastra Produtos com PK = offer['id'].
    Tenta usar offer['name'] como name.
    Retorna quantos foram criados.
    """
    created = 0

    for offer in offers:
        offer_id = offer.get("id")
        if not offer_id:
            continue

        name = offer.get("name")

        existing = session.execute(
            select(Produto).where(Produto.offer_id == offer_id)
        ).scalar_one_or_none()

        if existing is None:
            session.add(Produto(offer_id=offer_id, name=name))
            created += 1
        else:
            # atualiza nome se mudou
            existing.name = name

    return created


def upsert_sales(session, sales: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Para cada sale:
      - cria/atualiza Cliente (payer)
      - cria/atualiza Venda (lancamento)
    Retorna contagem de criados/atualizados.
    """
    res = {
        "clientes_criados": 0,
        "clientes_atualizados": 0,
        "vendas_criadas": 0,
        "vendas_atualizadas": 0,
    }

    for sale in sales:
        sale_id = sale.get("id")
        if not sale_id:
            continue

        # ---------- Cliente ----------
        payer = (sale.get("payer") or {})
        payer_identity = (payer.get("identity") or {})

        payer_id = payer.get("id")
        if not payer_id:
            # sem payer_id não dá pra vincular
            continue

        payer_cnpj = payer_identity.get("document")
        payer_nome = payer_identity.get("fullName")
        payer_email = payer_identity.get("email")

        cliente = session.execute(
            select(Cliente).where(Cliente.payer_id == payer_id)
        ).scalar_one_or_none()

        if cliente is None:
            session.add(
                Cliente(
                    payer_id=payer_id,
                    cnpj=payer_cnpj,
                    nome=payer_nome,
                    email=payer_email,
                )
            )
            res["clientes_criados"] += 1
        else:
            cliente.cnpj = payer_cnpj
            cliente.nome = payer_nome
            cliente.email = payer_email
            res["clientes_atualizados"] += 1

        # ---------- Dados da venda ----------
        installment_fee_cents = int(((sale.get("amount") or {}).get("installmentFeeCents")) or 0)
        payment_method = sale.get("paymentMethod")
        created_at = parse_created_at(sale.get("createdAt"))

        # item principal (como você fez)
        item0 = (sale.get("items") or [None])[0] or {}
        offer_id = item0.get("offerId")
        price_cents = int(item0.get("priceCents") or 0)
        product_name = item0.get("productName")

        if not offer_id:
            # sem offer_id não dá pra vincular ao produto
            continue

        # garante que o produto exista (caso não tenha rodado upsert_offers antes)
        prod = session.execute(
            select(Produto).where(Produto.offer_id == offer_id)
        ).scalar_one_or_none()
        if prod is None:
            session.add(Produto(offer_id=offer_id, name=product_name))

        raw_json = json.dumps(sale, ensure_ascii=False)

        venda = session.execute(
            select(Venda).where(Venda.sale_id == sale_id)
        ).scalar_one_or_none()

        if venda is None:
            session.add(
                Venda(
                    sale_id=sale_id,
                    payer_id=payer_id,
                    offer_id=offer_id,
                    installment_fee_cents=installment_fee_cents,
                    payment_method=payment_method,
                    price_cents=price_cents,
                    product_name=product_name,
                    created_at=created_at,
                    raw_json=raw_json,
                )
            )
            res["vendas_criadas"] += 1
        else:
            # atualiza campos (sem criar duplicidade)
            venda.payer_id = payer_id
            venda.offer_id = offer_id
            venda.installment_fee_cents = installment_fee_cents
            venda.payment_method = payment_method
            venda.price_cents = price_cents
            venda.product_name = product_name
            venda.created_at = created_at
            venda.raw_json = raw_json
            res["vendas_atualizadas"] += 1

    return res
