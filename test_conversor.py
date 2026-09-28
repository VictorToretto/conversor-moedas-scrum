"""
Testes unitários do conversor de moedas (framework unittest).

Cada teste indica o critério de aceitação (CA) que verifica.
Para rodar: python -m unittest -v
"""

import unittest
import urllib.error
from decimal import Decimal
from unittest.mock import MagicMock, patch

import conversor
from conversor import (
    TAXAS_FIXAS,
    arredondar,
    converter,
    escolher_moeda,
    formatar,
    ler_valor,
    obter_taxas,
)


class TestConversao(unittest.TestCase):
    """CA01, CA03, CA04 e CA05: cálculo da conversão."""

    def test_dolar_para_real(self):
        # CA03: 100 USD com taxa 5,1888 = 518,88 BRL
        self.assertEqual(converter(Decimal("100"), "USD", "BRL"), Decimal("518.88"))

    def test_real_para_dolar(self):
        # CA03: 100 / 5,1888 = 19,272... -> 19,27
        self.assertEqual(converter(Decimal("100"), "BRL", "USD"), Decimal("19.27"))

    def test_euro_para_real(self):
        # CA03: taxa cruzada EUR -> BRL = 5,1888 / 0,87722
        self.assertEqual(converter(Decimal("50"), "EUR", "BRL"), Decimal("295.75"))

    def test_mesma_moeda(self):
        # CA01: origem igual ao destino devolve o mesmo valor
        self.assertEqual(converter(Decimal("10"), "BRL", "BRL"), Decimal("10.00"))

    def test_aceita_codigo_em_minusculas(self):
        # CA01
        self.assertEqual(converter(Decimal("100"), "usd", "brl"), Decimal("518.88"))

    def test_resultado_com_duas_casas(self):
        # CA04: o resultado sempre tem 2 casas decimais
        resultado = converter(Decimal("1"), "USD", "USD")
        self.assertEqual(str(resultado), "1.00")

    def test_arredondamento_meio_para_cima(self):
        # CA05: 1,845 -> 1,85 e 2,675 -> 2,68 (com float, round(2.675, 2) daria 2.67)
        self.assertEqual(arredondar(Decimal("1.845")), Decimal("1.85"))
        self.assertEqual(arredondar(Decimal("2.675")), Decimal("2.68"))
        self.assertEqual(arredondar(Decimal("1.844")), Decimal("1.84"))

    def test_arredonda_so_no_final(self):
        # CA05: com taxa 1,5, converter 1,23 dá 1,845 -> 1,85
        taxas = {"USD": Decimal("1"), "BRL": Decimal("1.5"), "EUR": Decimal("1")}
        self.assertEqual(converter(Decimal("1.23"), "USD", "BRL", taxas), Decimal("1.85"))

    def test_moeda_nao_suportada(self):
        # CA01 (negativo)
        with self.assertRaises(ValueError):
            converter(Decimal("10"), "XYZ", "BRL")

    def test_valor_zero_ou_negativo(self):
        # CA02 (negativo)
        for valor in (Decimal("0"), Decimal("-5")):
            with self.assertRaises(ValueError):
                converter(valor, "USD", "BRL")


class TestEntradaEFormatacao(unittest.TestCase):
    """CA02 e CA03: leitura do valor digitado e exibição do resultado."""

    def test_aceita_virgula_e_ponto(self):
        # CA02
        self.assertEqual(ler_valor("10,50"), Decimal("10.50"))
        self.assertEqual(ler_valor("10.50"), Decimal("10.50"))
        self.assertEqual(ler_valor("  7 "), Decimal("7"))

    def test_rejeita_texto_invalido(self):
        # CA02 (negativo)
        for texto in ("abc", "", "10 reais"):
            with self.assertRaises(ValueError):
                ler_valor(texto)

    def test_rejeita_zero_e_negativo(self):
        # CA02 (negativo)
        for texto in ("0", "-3"):
            with self.assertRaises(ValueError):
                ler_valor(texto)

    def test_formatacao_padrao_brasileiro(self):
        # CA03 e CA04
        self.assertEqual(formatar(Decimal("1234.5"), "BRL"), "1.234,50 BRL")
        self.assertEqual(formatar(Decimal("10"), "USD"), "10,00 USD")


class TestTaxasDaAPI(unittest.TestCase):
    """CA06 e CA07: acesso à API e taxas de reserva (a internet é simulada com mock)."""

    RESPOSTA_API = (
        b'[{"date": "2026-09-28", "base": "USD", "quote": "BRL", "rate": 5.30},'
        b' {"date": "2026-09-28", "base": "USD", "quote": "EUR", "rate": 0.90}]'
    )

    def resposta_falsa(self, conteudo):
        """Cria um objeto que imita a resposta do urlopen."""
        resposta = MagicMock()
        resposta.__enter__.return_value.read.return_value = conteudo
        return resposta

    @patch("conversor.urllib.request.urlopen")
    def test_usa_taxas_atualizadas_da_api(self, urlopen_falso):
        # CA06: as taxas vêm da API quando ela responde
        urlopen_falso.return_value = self.resposta_falsa(self.RESPOSTA_API)
        taxas, fonte = obter_taxas()
        self.assertEqual(fonte, "API Frankfurter")
        self.assertEqual(taxas["BRL"], Decimal("5.30"))
        self.assertEqual(converter(Decimal("100"), "USD", "BRL", taxas), Decimal("530.00"))

    @patch("conversor.urllib.request.urlopen")
    def test_acessa_a_url_correta_com_tempo_limite(self, urlopen_falso):
        # CA06: a API é chamada com base USD e tempo limite de 5 segundos
        urlopen_falso.return_value = self.resposta_falsa(self.RESPOSTA_API)
        obter_taxas()
        urlopen_falso.assert_called_once_with(conversor.URL_API, timeout=5)
        self.assertIn("base=USD", conversor.URL_API)

    @patch("conversor.urllib.request.urlopen")
    def test_sem_internet_usa_taxas_fixas(self, urlopen_falso):
        # CA07: se a API não responder, usa as taxas fixas
        urlopen_falso.side_effect = urllib.error.URLError("sem conexão")
        taxas, fonte = obter_taxas()
        self.assertEqual(taxas, TAXAS_FIXAS)
        self.assertIn("taxas fixas", fonte)

    @patch("conversor.urllib.request.urlopen")
    def test_resposta_invalida_usa_taxas_fixas(self, urlopen_falso):
        # CA07: resposta que não é JSON ou sem todas as moedas -> taxas fixas
        for conteudo in (b"<html>erro</html>", b'[{"base": "USD", "quote": "BRL", "rate": 5}]'):
            urlopen_falso.return_value = self.resposta_falsa(conteudo)
            taxas, _ = obter_taxas()
            self.assertEqual(taxas, TAXAS_FIXAS)


class TestInterface(unittest.TestCase):
    """CA08: o menu responde de forma adequada (o teclado é simulado)."""

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["xyz", "9", "2"])
    def test_moeda_invalida_pergunta_de_novo(self, _input, print_falso):
        self.assertEqual(escolher_moeda("Moeda: "), "USD")
        self.assertEqual(print_falso.call_count, 2)  # duas mensagens de erro

    @patch("conversor.obter_taxas", return_value=(TAXAS_FIXAS, "taxas fixas"))
    @patch("builtins.input", side_effect=["2", "BRL", "abc", "100", "n"])
    @patch("builtins.print")
    def test_fluxo_completo(self, print_falso, _input, _taxas):
        conversor.main()
        textos = " ".join(str(c.args[0]) for c in print_falso.call_args_list if c.args)
        self.assertIn("Valor inválido", textos)
        self.assertIn("100,00 USD = 518,88 BRL", textos)
        self.assertIn("Até logo!", textos)


if __name__ == "__main__":
    unittest.main()
