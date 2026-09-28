# Revisão de código e documentação

Depois de terminar o código e os testes, revisei tudo usando o checklist abaixo e rodei os testes de novo.

## Checklist

| Item | Resultado |
|------|:---------:|
| O código atende a todos os critérios de aceitação? | ✅ |
| Todos os testes passam? (`python -m unittest`, 20 testes) | ✅ |
| As funções têm nomes claros e comentários explicando o que fazem? | ✅ |
| Os valores em dinheiro usam `Decimal` em vez de `float`? | ✅ |
| O programa trata erros sem travar (valor inválido, sem internet)? | ✅ |
| A documentação está de acordo com o código? | ✅ (após ajustes) |

## Problemas encontrados e corrigidos

1. **Erro no teste do menu:** o teste `test_fluxo_completo` quebrou porque o programa chama `print()` sem texto (para pular linha) e o teste tentava ler o texto de todas as chamadas. Corrigi o teste para ignorar essas chamadas.
2. **Taxas em `float` vindas da API:** o JSON traz números como `float`. Para não perder precisão, converto cada taxa com `Decimal(str(taxa))`.
3. **Enunciado com duas funcionalidades:** a parte de documentação pede o "login", mas a entrega é o conversor. Documentei os dois: o conversor completo e o login como proposta para a próxima sprint.

## Sugestões de melhoria

Estas sugestões foram adicionadas ao Backlog do quadro do Trello, para uma próxima sprint:

1. Criar uma janela gráfica (por exemplo, com Tkinter), além do terminal.
2. Guardar em arquivo a última cotação obtida, para usar quando estiver sem internet.
3. Implementar o login e o histórico de conversões, conforme a documentação técnica.
4. Aceitar valores com separador de milhar, como `1.234,56`.
5. Adicionar mais moedas (libra, iene etc.).
6. Rodar os testes automaticamente no GitHub a cada envio (GitHub Actions).
