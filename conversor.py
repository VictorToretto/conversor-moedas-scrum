"""
Conversor de Moedas - Atividade "Agile Docs & Code"
Autor: Victor Conceição

Converte valores entre Real (BRL), Dólar (USD) e Euro (EUR).
As taxas são buscadas na API Frankfurter. Se a API não responder
(por exemplo, sem internet), o programa usa taxas fixas de referência.
"""

import json
import urllib.request
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

MOEDAS = {
    "BRL": "Real brasileiro",
    "USD": "Dólar americano",
    "EUR": "Euro",
}

# Taxas de referência: quanto vale 1 dólar em cada moeda (cotação de 28/09/2026).
# São usadas quando não é possível acessar a API.
TAXAS_FIXAS = {
    "USD": Decimal("1"),
    "BRL": Decimal("5.1888"),
    "EUR": Decimal("0.87722"),
}

URL_API = "https://api.frankfurter.dev/v2/rates?base=USD&quotes=BRL,EUR"


def buscar_taxas_api(url=URL_API, tempo_limite=5):
    """Busca as taxas atuais na API Frankfurter.

    Retorna um dicionário no formato {moeda: taxa}, com base no dólar.
    A API responde uma lista como:
    [{"date": "2026-09-28", "base": "USD", "quote": "BRL", "rate": 5.1888}, ...]
    """
    with urllib.request.urlopen(url, timeout=tempo_limite) as resposta:
        dados = json.loads(resposta.read())

    taxas = {"USD": Decimal("1")}
    for item in dados:
        # str() evita erros de arredondamento do float (ex.: 5.1888 vira "5.1888")
        taxas[item["quote"]] = Decimal(str(item["rate"]))
    return taxas


def obter_taxas():
    """Tenta usar a API; se der erro, usa as taxas fixas.

    Retorna uma tupla (taxas, fonte), onde fonte diz de onde vieram as taxas.
    """
    try:
        taxas = buscar_taxas_api()
        if all(moeda in taxas for moeda in MOEDAS):
            return taxas, "API Frankfurter"
    except (OSError, ValueError, KeyError, TypeError):
        # OSError: sem internet ou tempo esgotado; ValueError: resposta que não é JSON;
        # KeyError/TypeError: resposta em formato diferente do esperado.
        pass
    return TAXAS_FIXAS, "taxas fixas de referência (valor aproximado)"


def ler_valor(texto):
    """Converte o valor digitado em Decimal. Aceita vírgula ou ponto como decimal."""
    texto = texto.strip().replace(",", ".")
    try:
        valor = Decimal(texto)
    except InvalidOperation:
        raise ValueError("Valor inválido. Digite um número, por exemplo 10,50.")
    if not valor.is_finite() or valor <= 0:
        raise ValueError("O valor deve ser um número maior que zero.")
    return valor


def arredondar(valor):
    """Arredonda para 2 casas decimais pela regra "meio para cima" (1,845 -> 1,85)."""
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def converter(valor, origem, destino, taxas=TAXAS_FIXAS):
    """Converte um valor da moeda de origem para a moeda de destino.

    As taxas estão todas em relação ao dólar, então a taxa entre duas
    moedas é: taxa do destino / taxa da origem.
    """
    origem = origem.upper()
    destino = destino.upper()
    for moeda in (origem, destino):
        if moeda not in MOEDAS:
            raise ValueError(f"Moeda não suportada: {moeda}. Use BRL, USD ou EUR.")
    if valor <= 0:
        raise ValueError("O valor deve ser um número maior que zero.")

    taxa = taxas[destino] / taxas[origem]
    return arredondar(valor * taxa)


def formatar(valor, moeda):
    """Formata no padrão brasileiro: 1234.5 -> '1.234,50 BRL'."""
    texto = f"{valor:,.2f}"  # 1,234.50
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{texto} {moeda}"


def escolher_moeda(pergunta):
    """Pergunta a moeda até o usuário digitar uma opção válida (número ou código)."""
    codigos = list(MOEDAS)
    while True:
        resposta = input(pergunta).strip().upper()
        if resposta.isdigit() and 1 <= int(resposta) <= len(codigos):
            return codigos[int(resposta) - 1]
        if resposta in MOEDAS:
            return resposta
        print("Opção inválida. Digite o número ou o código da moeda (ex.: 2 ou USD).")


def perguntar_valor(moeda):
    """Pergunta o valor até o usuário digitar um número válido."""
    while True:
        try:
            return ler_valor(input(f"Valor em {moeda}: "))
        except ValueError as erro:
            print(erro)


def main():
    print("=== Conversor de Moedas ===")
    taxas, fonte = obter_taxas()
    print(f"Taxas usadas: {fonte}")

    while True:
        print()
        for numero, (codigo, nome) in enumerate(MOEDAS.items(), start=1):
            print(f"  {numero}) {codigo} - {nome}")

        origem = escolher_moeda("Moeda de origem: ")
        destino = escolher_moeda("Moeda de destino: ")
        valor = perguntar_valor(origem)

        resultado = converter(valor, origem, destino, taxas)
        print(f"\n{formatar(valor, origem)} = {formatar(resultado, destino)}")

        if input("\nFazer outra conversão? (s/n): ").strip().lower() != "s":
            break

    print("Até logo!")


if __name__ == "__main__":
    main()
