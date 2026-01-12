# yuzer_main.py
"""
Integração Yuzer (API) -> SQLite (SQLAlchemy)

Pré-requisitos:
    pip install SQLAlchemy requests

Arquivos esperados:
    - yuzer_integration.py  (contém class YuzerIntegration)
    - yuzer_database.py     (contém Base, init_db, get_sessionmaker e models)
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, Optional

try:
    from sqlalchemy import select
except ModuleNotFoundError as e:
    raise SystemExit(
        "SQLAlchemy não está instalado.\n"
        "Instale com: pip install SQLAlchemy\n"
    ) from e

from yuzer_integration import YuzerIntegration
from yuzer_database import (
    init_db,
    get_engine,
    get_sessionmaker,
    parse_iso_datetime,
    YuzerEvent,
    YuzerProduct,
    YuzerEventProduct,
)


# -----------------------------
# Helpers de persistência
# -----------------------------
def upsert_yuzer_event(session, event: Dict[str, Any]) -> int:
    """
    Salva/atualiza um evento baseado no ID vindo da API.
    """
    event_id = int(event["id"])

    existing = session.execute(
        select(YuzerEvent).where(YuzerEvent.id == event_id)
    ).scalar_one_or_none()

    values = {
        "id": event_id,
        "name": event.get("name"),
        "description": event.get("description"),
        "status": bool(event.get("status")) if event.get("status") is not None else None,
        "updated_at": parse_iso_datetime(event.get("updatedAt")),
        "raw_json": json.dumps(event, ensure_ascii=False),
    }

    if existing is None:
        session.add(YuzerEvent(**values))
    else:
        for k, v in values.items():
            setattr(existing, k, v)

    return event_id


def upsert_yuzer_product(session, product: Dict[str, Any]) -> int:
    """
    Salva/atualiza um produto do catálogo baseado no ID vindo da API.
    """
    product_id = int(product["id"])

    existing = session.execute(
        select(YuzerProduct).where(YuzerProduct.id == product_id)
    ).scalar_one_or_none()

    # Brand/Category/Subcategory vêm como dicts no catálogo
    brand = product.get("brand") or {}
    category = product.get("category") or {}
    subcategory = product.get("subcategory") or {}

    values = {
        "id": product_id,
        "name": product.get("name"),
        "description": product.get("description"),
        "type": product.get("type"),
        "status": bool(product.get("status")) if product.get("status") is not None else None,
        "measure_unit": product.get("measureUnit"),
        "control_size": bool(product.get("controlSize")) if product.get("controlSize") is not None else None,
        "image": product.get("image"),
        "price": product.get("price"),
        "cost": product.get("cost"),

        "brand_id": brand.get("id"),
        "brand_name": brand.get("name"),
        "brand_description": brand.get("description"),

        "category_id": category.get("id"),
        "category_name": category.get("name"),
        "category_description": category.get("description"),

        "subcategory_id": subcategory.get("id"),
        "subcategory_name": subcategory.get("name"),
        "subcategory_description": subcategory.get("description"),

        "raw_json": json.dumps(product, ensure_ascii=False),
    }

    if existing is None:
        session.add(YuzerProduct(**values))
    else:
        for k, v in values.items():
            setattr(existing, k, v)

    return product_id


def insert_event_products_snapshot(session, event_id: int, content: list[Dict[str, Any]]) -> int:
    """
    Snapshot: insere exatamente o content do endpoint do evento.
    Não deduplica.
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
            raw_json=json.dumps(item, ensure_ascii=False),
        )
        session.add(row)
        inserted += 1
    return inserted


# -----------------------------
# Rotinas de coleta
# -----------------------------
def sync_catalog_products(
    yuzer: YuzerIntegration,
    session,
    *,
    per_page: int = 50,
    max_pages: Optional[int] = None
) -> int:
    """
    Varre o catálogo de produtos e salva/atualiza.
    """
    total_saved = 0
    page = 1

    while True:
        resp = yuzer.get_products(page=page, per_page=per_page)
        content = resp.get("content") or []
        if not content:
            break

        for p in content:
            upsert_yuzer_product(session, p)
            total_saved += 1

        # paginação
        last = bool(resp.get("last"))
        if last:
            break

        page += 1
        if max_pages and page > max_pages:
            break

    return total_saved


def sync_events(
    yuzer: YuzerIntegration,
    session,
    *,
    per_page: int = 50,
    max_pages: Optional[int] = None
) -> int:
    """
    Varre eventos e salva/atualiza.
    """
    total_saved = 0
    page = 1

    while True:
        resp = yuzer.get_events(page=page, per_page=per_page)
        content = resp.get("content") or []
        if not content:
            break

        for ev in content:
            upsert_yuzer_event(session, ev)
            total_saved += 1

        last = bool(resp.get("last"))
        if last:
            break

        page += 1
        if max_pages and page > max_pages:
            break

    return total_saved


def sync_event_products(
    yuzer: YuzerIntegration,
    session,
    *,
    event_id: int,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    per_page: int = 200,
    max_pages: Optional[int] = 1
    ) -> int:
    """
    Puxa produtos por evento e grava snapshot no banco.
    """
    total_inserted = 0
    page = 1

    while True:
        resp = yuzer.get_event_products(
            event_id,
            page=page,
            per_page=per_page,
            date_from=date_from,
            date_to=date_to,
        )

        print(f'A resp é {resp}')

        content = resp.get("content") or []
        if not content:
            break

        total_inserted += insert_event_products_snapshot(session, event_id, content)

        last = bool(resp.get("last"))
        if last:
            break

        page += 1
        if page > max_pages:
            break

    return total_inserted
# -----------------------------
# Main
# -----------------------------
def main():
    # credenciais
    username = "financeiroverrieverri@gmail.com"
    password = "Bpo@123"

    # filtros opcionais para o endpoint de produtos do evento
    # (use seus valores quando precisar)
    date_from = "2026-01-08T16:00:00.000Z"
    date_to = "2026-01-11T05:00:00.000Z"
    id = '25574'

    # 1) API client
    yuzer = YuzerIntegration(username, password)
    yuzer.authenticate()

    # 2) Banco
    engine = get_engine("sqlite:///yuzer.sqlite")
    init_db(engine)
    SessionLocal = get_sessionmaker(engine)

    with SessionLocal() as session:
        # A) sincroniza eventos
        events_saved = sync_events(yuzer, session, per_page=50)
        # B) sincroniza catálogo de produtos (opcional, mas útil)
        products_saved = sync_catalog_products(yuzer, session, per_page=50)
        session.commit()

        
        print(f"[OK] Eventos salvos/atualizados: {events_saved}")
        print(f"[OK] Produtos (catálogo) salvos/atualizados: {products_saved}")

        # C) exemplo: pega 1 evento do banco e salva snapshot de produtos dele
        #    (você pode trocar para iterar todos, ou filtrar por status, etc.)
        #first_event = session.execute(select(YuzerEvent).order_by(YuzerEvent.id.desc())).scalars().first()
        first_event = session.execute(select(YuzerEvent).where(YuzerEvent.id == id)).scalar_one_or_none()
        print(first_event)
        if not first_event:
            print("[WARN] Nenhum evento no banco para puxar produtos.")
            return

        event_id = first_event.id
        inserted = sync_event_products(
            yuzer,
            session,
            event_id=event_id,
            date_from=date_from,
            date_to=date_to,
            per_page=200,
        )

        session.commit()

        print(f"[OK] Snapshot produtos do evento {event_id}: inseridos {inserted} registros.")


if __name__ == "__main__":
    main()
