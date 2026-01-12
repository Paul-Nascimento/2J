from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    Index,
    create_engine,
    select,
)
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, sessionmaker


# -------------------------
# Base / Engine / Session
# -------------------------
#class Base(DeclarativeBase):
#    pass

Base = declarative_base()

def get_engine(db_url: str = "sqlite:///yuzer.sqlite"):
    return create_engine(db_url, echo=False, future=True)


def get_sessionmaker(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db(engine):
    Base.metadata.create_all(engine)


# -------------------------
# Helpers
# -------------------------
def parse_iso_z(dt_str: Optional[str]) -> Optional[datetime]:
    """
    Ex: "2026-01-11T03:02:46.681921Z"
    """
    if not dt_str:
        return None
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))

def parse_iso_datetime(value: str | None):
    """
    Aceita:
      - '2026-01-11T03:02:46.681921Z'
      - '2025-12-26T15:40:45.000Z'
      - ou None
    Retorna datetime (UTC) ou None.
    """
    if not value:
        return None
    # remove Z e normaliza
    value = value.replace("Z", "+00:00")
    return datetime.fromisoformat(value)

def jdump(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False)


# -------------------------
# Models
# -------------------------
class YuzerProduct(Base):
    __tablename__ = "yuzer_products"

    # campos diretos do produto
    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # product['id']
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    measure_unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)     # measureUnit
    status: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)             # status
    type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)             # type
    control_size: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)       # controlSize
    image: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)          # image (quando existir)

    # brand (objeto aninhado)
    brand_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    brand_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    brand_description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # category (objeto aninhado)
    category_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    category_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    category_description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # subcategory (objeto aninhado)
    subcategory_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    subcategory_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    subcategory_description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # opcional: json bruto do item de content
    raw_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class YuzerEvent(Base):
    __tablename__ = "yuzer_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # event['id']
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    status: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # opcional: json bruto do item de content
    raw_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


# -------------------------
# Upserts (baseado em content)
# -------------------------
def upsert_products(session, content: List[Dict[str, Any]], *, save_raw: bool = True) -> Dict[str, int]:
    """
    Recebe SOMENTE a lista content do endpoint de products.
    Exemplo: data['content']
    """
    res = {"created": 0, "updated": 0}

    for p in content:
        pid = p.get("id")
        if pid is None:
            continue

        brand = p.get("brand") or {}
        category = p.get("category") or {}
        subcategory = p.get("subcategory") or {}

        existing = session.execute(
            select(YuzerProduct).where(YuzerProduct.id == int(pid))
        ).scalar_one_or_none()

        values = dict(
            id=int(pid),
            name=p.get("name") or "",
            description=p.get("description"),

            cost=p.get("cost"),
            price=p.get("price"),

            measure_unit=p.get("measureUnit"),
            status=p.get("status"),
            type=p.get("type"),
            control_size=p.get("controlSize"),
            image=p.get("image"),

            brand_id=brand.get("id"),
            brand_name=brand.get("name"),
            brand_description=brand.get("description"),

            category_id=category.get("id"),
            category_name=category.get("name"),
            category_description=category.get("description"),

            subcategory_id=subcategory.get("id"),
            subcategory_name=subcategory.get("name"),
            subcategory_description=subcategory.get("description"),

            raw_json=jdump(p) if save_raw else None,
        )

        if existing is None:
            session.add(YuzerProduct(**values))
            res["created"] += 1
        else:
            for k, v in values.items():
                setattr(existing, k, v)
            res["updated"] += 1

    return res


def upsert_events(session, content: List[Dict[str, Any]], *, save_raw: bool = True) -> Dict[str, int]:
    """
    Recebe SOMENTE a lista content do endpoint de events (salesPanels/search).
    Exemplo: data['content']
    """
    res = {"created": 0, "updated": 0}

    for e in content:
        eid = e.get("id")
        if eid is None:
            continue

        existing = session.execute(
            select(YuzerEvent).where(YuzerEvent.id == int(eid))
        ).scalar_one_or_none()

        values = dict(
            id=int(eid),
            name=e.get("name") or "",
            description=e.get("description"),
            status=e.get("status"),
            updated_at=parse_iso_datetime(e.get("updatedAt")),
            raw_json=jdump(e) if save_raw else None,
        )

        if existing is None:
            session.add(YuzerEvent(**values))
            res["created"] += 1
        else:
            for k, v in values.items():
                setattr(existing, k, v)
            res["updated"] += 1

    return res





# Assumindo que você já tem Base no seu arquivo


class YuzerEventProduct(Base):
    __tablename__ = "yuzer_event_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # vínculo com o evento
    event_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)

    # campos que vêm no "content"
    product_id: Mapped[Optional[int]] = mapped_column(Integer, index=True, nullable=True)  # productId

    total: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    unit_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # unitPrice
    tax: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    brand: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    image: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    returned_quantity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # returnedQuantity
    returned_total: Mapped[Optional[float]] = mapped_column(Float, nullable=True)    # returnedTotal

    discount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)        # totalCost
    discount_quantity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # discountQuantity

    remaining_total: Mapped[Optional[float]] = mapped_column(Float, nullable=True)   # remainingTotal
    remaining_quantity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)# remainingQuantity

    cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # opcional (recomendado): item bruto para auditoria
    raw_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


def insert_event_products(
    session,
    event_id: int,
    content: List[Dict[str, Any]],
    *,
    save_raw: bool = True
) -> int:
    """
    Insere "do jeito que vier" da API (content), adicionando apenas event_id.
    Não deduplica e não valida repetição.
    """
    inserted = 0

    for item in content:
        row = YuzerEventProduct(
            event_id=int(event_id),
            product_id=item.get("productId"),

            total=item.get("total"),
            price=item.get("price"),
            unit_price=item.get("unitPrice"),
            tax=item.get("tax"),
            count=item.get("count"),

            category=item.get("category"),
            subcategory=item.get("subcategory"),
            brand=item.get("brand"),
            name=item.get("name"),

            image=item.get("image"),
            type=item.get("type"),

            returned_quantity=item.get("returnedQuantity"),
            returned_total=item.get("returnedTotal"),

            discount=item.get("discount"),
            total_cost=item.get("totalCost"),
            discount_quantity=item.get("discountQuantity"),

            remaining_total=item.get("remainingTotal"),
            remaining_quantity=item.get("remainingQuantity"),

            cost=item.get("cost"),

            raw_json=json.dumps(item, ensure_ascii=False) if save_raw else None,
        )

        session.add(row)
        inserted += 1

    return inserted
