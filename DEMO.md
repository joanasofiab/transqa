# Demo — TransQA

Este ficheiro documenta uma execução típica do TransQA em:
- **Single segment** (1 par de textos)
- **Batch mode** (CSV com vários segmentos)

---

## 1) Single segment

**Perfil:** Default  
**Par linguístico:** EN->PT

### Como correr

Executar a app:

```powershell
streamlit run app.py
````

Na interface:

1. Perfil = **Default**
2. Par linguístico = **EN->PT**
3. Colar os textos abaixo em *Source* e *Target*
4. Clicar em **Analisar**
5. Exportar **CSV** e **HTML** (botões de download)

### Source

```text
Hello {name}, your balance is € 1,250.50 due on 03/04/2026.
Please confirm at https://example.com/account or email help@company.com.
```

### Target (com erros propositados)

```text
Olá, o seu saldo é 1.250,50 € com vencimento em 03/04/2026.
Por favor confirme em https://example.com/account ou contacte help@company.com.
```

### O que validar (esperado)

* **Placeholders**: `{name}` deve ser preservado (neste exemplo foi omitido → deve gerar alerta).
* **Currencies/Numbers**: o montante deve manter-se (normalização EN/PT; símbolo pode surgir antes/depois).
* **Non-translate**: URL e email devem manter-se.
* **Dates**: a data numérica pode ser sinalizada como ambígua (dependendo da configuração).

### Outputs (downloads)

* `transqa_report.csv`
* `transqa_report.html`

---

## 2) Batch mode (CSV)

**Ficheiro de exemplo:** `data/batch_example.csv`

### Como usar

Na interface, na secção **Batch mode (CSV)**:

1. Carregar `data/batch_example.csv`
2. Clicar em **Analisar CSV (Batch)**
3. Fazer download dos outputs

### O que validar (esperado)

* **Resumo por linha**: nº de alertas e contagem por severidade.
* **Alertas detalhados**: inclui `row_id` e `pair` (quando existir no CSV).

### Outputs (downloads)

* `transqa_batch_summary.csv`
* `transqa_batch_alerts.csv`
* `transqa_batch_alerts.html`