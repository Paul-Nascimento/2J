from hubla_integration import HublaIntegration
from hubla_database import make_engine, make_session_factory, init_db, upsert_offers, upsert_sales

hubla = HublaIntegration(
    "financeiro@jovemdovinho.com.br",
    "2jFinanceiro",
    "AIzaSyCQZKqdJO5aV64PEiWYrTZChJ3UP33-lB8",
    "eSLHOduIf1VueToaTj2b2B0fARP2"
)
hubla.authenticate()

offers = hubla.get_offers()
offers_id = hubla.get_offer_ids()
sales = hubla.get_sales(offers_id, "01/12/2025", "12/01/2026")

engine = make_engine("hubla_database.sqlite")
init_db(engine)
Session = make_session_factory(engine)

with Session() as session:
    #upsert_offers(session, offers)
    res = upsert_sales(session, sales)
    session.commit()

#print(res)
