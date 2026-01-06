# -*- coding: utf-8 -*-
import smtplib
from email.message import EmailMessage
from typing import Sequence, Optional, Mapping, Iterable

# ---------- Helpers de renderização ----------

_EXPECTED_COLS = ("productId", "productName", "productCategory")

def _coalesce(d: Mapping, keys: Iterable[str], default: str = "") -> str:
    """Retorna o primeiro valor encontrado considerando variações de caso/underscore."""
    lk = {k.lower().replace("-", "").replace("_", ""): k for k in d.keys()}
    for k in keys:
        norm = k.lower().replace("-", "").replace("_", "")
        if norm in lk:
            v = d[lk[norm]]
            return "" if v is None else str(v)
    return default

def _normalize_row(row: Mapping) -> tuple[str, str, str]:
    """Extrai (productId, productName, productCategory) aceitando variações de chave."""
    pid = _coalesce(row, ["productId", "id", "product_id", "sku", "codigo"])
    pname = _coalesce(row, ["productName", "name", "product_name", "descricao"])
    pcat = _coalesce(row, ["productCategory", "category", "product_category", "categoria"])
    return pid, pname, pcat

def _render_table_text(rows: Sequence[Mapping]) -> str:
    header = "\t".join(_EXPECTED_COLS)
    lines = [header]
    for r in rows:
        pid, pname, pcat = _normalize_row(r)
        lines.append("\t".join([pid, pname, pcat]))
    return "\n".join(lines) if rows else "(sem registros)"

def _render_table_html(rows: Sequence[Mapping]) -> str:
    if not rows:
        return "<p><em>(sem registros)</em></p>"
    trs = []
    for r in rows:
        pid, pname, pcat = _normalize_row(r)
        trs.append(
            f"<tr>"
            f"<td style='padding:6px 8px;border:1px solid #ddd;'>{pid}</td>"
            f"<td style='padding:6px 8px;border:1px solid #ddd;'>{pname}</td>"
            f"<td style='padding:6px 8px;border:1px solid #ddd;'>{pcat}</td>"
            f"</tr>"
        )
    thead = (
        "<thead><tr>"
        + "".join(
            f"<th style='text-align:left;padding:8px;border:1px solid #ddd;background:#f6f6f6;'>{col}</th>"
            for col in _EXPECTED_COLS
        )
        + "</tr></thead>"
    )
    tbody = "<tbody>" + "".join(trs) + "</tbody>"
    return (
        "<table style='border-collapse:collapse;font-family:Arial,Helvetica,sans-serif;"
        "font-size:14px;margin-top:8px;'>" + thead + tbody + "</table>"
    )

def _render_email_body_produto(
    registros: Sequence[Mapping],
    numero_pedido: Optional[str] = None,
    previsao_faturamento: Optional[str] = None,
) -> tuple[str, str]:
    # Campos automáticos quando não informados
    num_ped = numero_pedido or "preenchido automaticamente pela automação"
    prev_fat = previsao_faturamento or "preenchido automaticamente pela automação"

    tabela_txt = _render_table_text(registros)
    tabela_html = _render_table_html(registros)

    # ----- Plain text -----
    plain = f"""Olá, 2J!

ALERTA DE CRIAÇÃO DE PRODUTO NO PATINHO FEIO!!

Houve uma criação de produto na Zig e, pela automação, o produto já foi criado na Omiê, mas atente-se: é necessário validar o preenchimento dos impostos.

Resumo do que deve ser validado:
- ICMS: Situação Tributária do ICMS Simples Nacional (CSOSN) e Origem
- PIS: Situação Tributária do PIS e Tipo de Cálculo para o PIS
- COFINS: Situação Tributária do COFINS e Tipo de Cálculo para o COFINS

Caminho para validação:
Painel Omiê -> Vendas e NF-e -> Venda de Produto -> Exibir todas -> Previsão de faturamento ou Número do Pedido de Venda -> Clique duas vezes no pedido criado e valide.

Número do pedido de venda: {num_ped}
Previsão de faturamento: {prev_fat}

Produtos criados (tabela):
{tabela_txt}

Informações dos impostos para validação:
- Cervejas e chopps: CFOP 5405, ICMS 500, NCM 22030000, PIS/COFINS 4
- Alimentos: CFOP 5102, ICMS 102, NCM 21069090, PIS/COFINS 99
- Drinks: CFOP 5405, ICMS 500, NCM 22089000, PIS/COFINS 99

Em caso de dúvidas, procure seu Gerente.
"""

    # ----- HTML -----
    html = f"""<!doctype html>
<html lang="pt-br">
  <body style="font-family:Arial,Helvetica,sans-serif; line-height:1.5;">
    <p>Olá, 2J!</p>
    <h2 style="margin:0;">ALERTA DE CRIAÇÃO DE PRODUTO NO PATINHO FEIO!!</h2>

    <p>
      Houve uma criação de produto na Zig e, pela automação, o produto já foi criado na Omiê,
      mas atente-se: <strong>é necessário validar o preenchimento dos impostos</strong>.
    </p>

    <h3 style="margin-bottom:4px;">Resumo do que deve ser validado</h3>
    <ul>
      <li><strong>ICMS</strong> — CSOSN e Origem;</li>
      <li><strong>PIS</strong> — Situação Tributária e Tipo de Cálculo;</li>
      <li><strong>COFINS</strong> — Situação Tributária e Tipo de Cálculo.</li>
    </ul>

    <h3 style="margin-bottom:4px;">Caminho para validação</h3>
    <p>Painel Omiê → Vendas e NF-e → Venda de Produto → Exibir todas → Previsão de faturamento ou Número do Pedido de Venda → Clique duas vezes no pedido criado e valide.</p>

    <p><strong>Número do pedido de venda:</strong> {num_ped}<br>
       <strong>Previsão de faturamento:</strong> {prev_fat}</p>

    <h3 style="margin-bottom:4px;">Produtos criados</h3>
    {tabela_html}

    <h3 style="margin-bottom:4px;">Informações dos impostos para validação</h3>
    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
      <thead>
        <tr>
          <th>Categoria</th><th>CFOP</th><th>ICMS</th><th>NCM</th><th>PIS/COFINS</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>Cervejas e chopps</td><td>5405</td><td>500</td><td>22030000</td><td>4</td></tr>
        <tr><td>Alimentos</td><td>5102</td><td>102</td><td>21069090</td><td>99</td></tr>
        <tr><td>Drinks</td><td>5405</td><td>500</td><td>22089000</td><td>99</td></tr>
      </tbody>
    </table>

    <p style="margin-top:16px;">Em caso de dúvidas, procure seu Gerente.</p>
  </body>
</html>
"""
    return plain, html

# ---------- Função principal de envio ----------

def send_product_creation_alert(
    destinatarios: Sequence[str],
    registros: Sequence[Mapping],
    smtp_host: str = "smtp.gmail.com",
    smtp_port: int = 587,
    smtp_user: str = "financeiropatinhofeio@gmail.com",
    smtp_password: str = "",  # use variável de ambiente
    remetente: str = "Alertas Patinho Feio <financeiropatinhofeio@gmail.com>",
    cc: Optional[Sequence[str]] = None,
    bcc: Optional[Sequence[str]] = None,
    numero_pedido: Optional[str] = None,
    previsao_faturamento: Optional[str] = None,
    assunto_prefixo: str = "Alerta: Produto criado na Zig / Validar impostos no Omiê",
    usar_starttls: bool = True,
) -> None:
    """
    Envia o e-mail de alerta (sem anexos), recebendo uma lista de dicionários e
    renderizando uma tabela com as colunas (productId, productName, productCategory).

    Exemplo de 'registros':
      [
        {"productId": "123", "productName": "Cerveja Pilsen 600ml", "productCategory": "Cervejas e chopps"},
        {"id": "456", "name": "Combo Petiscos", "categoria": "Alimentos"},
      ]
    """
    if not smtp_password:
        raise ValueError("Defina a senha SMTP (ex.: via variável de ambiente).")

    plain, html = _render_email_body_produto(
        registros=registros,
        numero_pedido=numero_pedido,
        previsao_faturamento=previsao_faturamento,
    )

    msg = EmailMessage()
    msg["Subject"] = f"{assunto_prefixo}"
    msg["From"] = remetente
    msg["To"] = ", ".join(destinatarios)
    if cc:
        msg["Cc"] = ", ".join(cc)

    all_rcpts = list(destinatarios) + (list(cc) if cc else []) + (list(bcc) if bcc else [])

    msg.set_content(plain)
    msg.add_alternative(html, subtype="html")

    if usar_starttls:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_password)
            server.send_message(msg, from_addr=remetente, to_addrs=all_rcpts)
    else:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.send_message(msg, from_addr=remetente, to_addrs=all_rcpts)

