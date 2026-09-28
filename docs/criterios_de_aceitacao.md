# Critérios de aceitação: conversor de moedas

**História de usuário:** como usuário, quero converter um valor de uma moeda para outra, para saber quanto ele vale na moeda de destino.

Moedas suportadas: **BRL** (Real), **USD** (Dólar) e **EUR** (Euro).

| ID | Critério | Exemplo |
|----|----------|---------|
| CA01 | O usuário seleciona a moeda de origem e a moeda de destino (pelo número do menu ou pelo código). Moeda inválida mostra mensagem de erro e pergunta de novo. | `2` ou `USD` seleciona o dólar; `XYZ` é recusado |
| CA02 | O usuário informa a quantidade na moeda de origem. Aceita vírgula ou ponto. Valores vazios, com letras, zero ou negativos são recusados com mensagem clara. | `10,50` e `10.50` são aceitos; `abc` e `-5` não |
| CA03 | O conversor exibe o valor equivalente na moeda de destino. | `100,00 USD = 518,88 BRL` |
| CA04 | O resultado tem precisão de, no mínimo, duas casas decimais. | `10` aparece como `10,00` |
| CA05 | O resultado é arredondado corretamente, pela regra "meio para cima", e só no final do cálculo. | `1,845` vira `1,85` |
| CA06 | As taxas são buscadas em uma API de câmbio, para ficarem atualizadas. | API Frankfurter |
| CA07 | Se a API não responder, o programa não trava: usa taxas fixas de referência e avisa o usuário. | sem internet, mostra "taxas fixas de referência" |
| CA08 | A interface é simples: menu numerado, mensagens em português e opção de fazer outra conversão. | `Fazer outra conversão? (s/n)` |

## Definição de pronto (Definition of Done)

Uma tarefa só vai para **Done** no Trello quando:

1. atende aos critérios acima;
2. tem testes passando (`python -m unittest`);
3. está documentada e enviada ao GitHub.

## Onde cada critério é testado

Todos os testes estão em [`test_conversor.py`](../test_conversor.py), e cada um tem um comentário com o critério que verifica.

| Critério | Testes |
|----------|--------|
| CA01 | `test_mesma_moeda`, `test_aceita_codigo_em_minusculas`, `test_moeda_nao_suportada` |
| CA02 | `test_aceita_virgula_e_ponto`, `test_rejeita_texto_invalido`, `test_rejeita_zero_e_negativo`, `test_valor_zero_ou_negativo` |
| CA03 | `test_dolar_para_real`, `test_real_para_dolar`, `test_euro_para_real`, `test_formatacao_padrao_brasileiro` |
| CA04 | `test_resultado_com_duas_casas`, `test_formatacao_padrao_brasileiro` |
| CA05 | `test_arredondamento_meio_para_cima`, `test_arredonda_so_no_final` |
| CA06 | `test_usa_taxas_atualizadas_da_api`, `test_acessa_a_url_correta_com_tempo_limite` |
| CA07 | `test_sem_internet_usa_taxas_fixas`, `test_resposta_invalida_usa_taxas_fixas` |
| CA08 | `test_moeda_invalida_pergunta_de_novo`, `test_fluxo_completo` |
