# TransQA — Quality Assurance (QA) para Tradução (EN/ES → PT)

TransQA é um protótipo de ferramenta de *Quality Assurance* para tradução, orientado a regras e configurável por cliente. O objetivo é detetar problemas frequentes em segmentos traduzidos (p.ex., números alterados, datas ambíguas, moedas/unidades omitidas, URLs/IDs não preservados), fornecendo alertas com evidências e sugestões de correção.

O projeto foi desenvolvido para ser **utilizável**, **reprodutível** e **facilmente extensível**, suportando perfis de configuração (por cliente/domínio) e avaliação automática com um conjunto “gold” de casos anotados.

---

## Funcionalidades principais

- **Checks implementados (rule-based)**
  - Dates (datas numéricas; deteção e aviso de ambiguidade)
  - Numbers (números gerais; com normalização PT/EN/ES e mitigação de falsos positivos em IDs)
  - Currencies (montantes monetários com símbolo antes/depois do número)
  - Percentages (percentagens: símbolo `%`)
  - Units (valores com unidade)
  - Ranges (intervalos: `10–15`, `10-15`)
  - Non-translate (URLs, Emails, IDs)

- **Configuração por perfil (YAML)**
  - ativar/desativar checks
  - definir símbolos monetários e lista de unidades
  - ajustar regras (p.ex., aviso de datas ambíguas)

- **Interface Streamlit**
  - introdução de texto fonte e tradução
  - execução de QA e visualização de alertas (tabela)

- **Avaliação automática (gold set)**
  - leitura de `data/gold_cases.csv`
  - execução por perfil
  - geração de resultados (`eval_results.csv`) e métricas (`eval_summary.txt`)

---

## Escopo e não-escopo

**Dentro do escopo**
- QA baseada em regras (regex + normalização) para fenómenos objetivos: números, datas, moedas, unidades, intervalos e itens “não traduzíveis”.
- Configuração por perfil de cliente/domínio.
- Avaliação reprodutível via conjunto de testes anotado.

**Fora do escopo (por desenho)**
- Avaliação semântica profunda (p.ex., “tradução correta” a nível de sentido)
- Ajustes automáticos ao texto alvo (o sistema apenas sinaliza)
- Integração direta com CAT tools (pode ser adicionada futuramente via CLI/API)

---

## Requisitos

- Python 3.10+ (recomendado)
- Dependências:
  - streamlit
  - pandas
  - pyyaml

---

## Instalação (Windows / PowerShell)

Na raiz do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install streamlit pandas pyyaml
```

---

## Quickstart (correr localmente)

```powershell
git clone https://github.com/joanasofiab/transqa.git
cd transqa
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py

---
## Avaliação (gold set)

```powershell
python -m eval.evaluate

---

## Executar a aplicação (Streamlit)

```powershell
streamlit run app.py
```

Abrir no browser: `http://localhost:8501`

---

## Estrutura do projeto (visão geral)

```
transqa/
  app.py
  config/
    default.yaml
    client_demo.yaml
  core/
    __init__.py
    models.py
    runner.py
  checks/
    __init__.py
    dates.py
    numbers.py
    currencies.py
    percentages.py
    units.py
    ranges.py
    nontranslate.py
    punctuation.py  (opcional)
  utils/
    __init__.py
    normalize.py
  data/
    gold_cases.csv
  eval/
    __init__.py
    evaluate.py
    eval_results.csv
    eval_summary.csv
    eval_summary.txt
```

---

## Arquitetura (como o sistema funciona)

1. **Configuração (YAML)** define quais os checks ativos e algumas regras (p.ex., símbolos monetários, unidades, datas ambíguas).
2. **Runner** (`core/runner.py`) recebe `source`, `target`, `pair` e `config`, executa os checks ativados e agrega alertas.
3. **Checks** (`checks/*.py`) devolvem uma lista de `Alert` (modelo em `core/models.py`) com:

   * severidade (`Critical`, `Warning`, `Info`)
   * nome do check
   * evidência no source/target
   * mensagem e sugestão
4. **UI** (`app.py`) apresenta os resultados em tabela.

---

## Perfis de configuração (YAML)

### Exemplo: `config/default.yaml` (padrão)

* checks ativos (lista `checks.enabled`)
* regras opcionais (`rules.*`), por exemplo:

  * `warn_ambiguous_numeric_dates: true`
  * `currency_symbols: ["€", "$", "£"]`
  * `units: ["°C", "mg", "kg", "cm", "mm"]`

Para correr a UI com outro perfil, basta apontar a UI para esse ficheiro (ou alterar a seleção na interface, se existir).

---

## Avaliação automática (gold set)

O gold set está em:

* `data/gold_cases.csv`

O script:

* `eval/evaluate.py`

### Correr avaliação (perfil default)

```powershell
python -m eval.evaluate
```

### Correr avaliação (perfil client_demo)

```powershell
$env:TRANSQA_CONFIG="config\client_demo.yaml"
python -m eval.evaluate
```

### Outputs gerados

* `eval/eval_results.csv` — resultados por caso (`expected_checks`, `predicted_checks`, `n_alerts`)
* `eval/eval_summary.csv` — TP/FP/FN e precisão/recall/F1 por check
* `eval/eval_summary.txt` — resumo legível no terminal/relatório

**Nota metodológica**: o cálculo é “case-level”: um check conta como correto se pelo menos um alerta desse tipo for emitido no segmento.

---

## Como adicionar um novo check (extensão)

### 1) Criar um ficheiro em `checks/`

Exemplo: `checks/placeholders.py`

Assinatura recomendada:

```python
from typing import List
from core.models import Alert

def check_placeholders(source: str, target: str) -> List[Alert]:
    alerts: List[Alert] = []
    # ... lógica ...
    return alerts
```

### 2) Ligar o check no runner (`core/runner.py`)

* importar a função
* adicionar uma condição baseada em `config["checks"]["enabled"]`

Exemplo:

```python
from checks.placeholders import check_placeholders

if "placeholders" in enabled:
    alerts += check_placeholders(source, target)
```

### 3) Ativar no YAML

Em `config/default.yaml`:

```yaml
checks:
  enabled:
    - placeholders
```

### 4) Adicionar casos ao gold set

Acrescentar exemplos em `data/gold_cases.csv` e correr:

```powershell
python -m eval.evaluate
```

---

## Boas práticas adotadas

* **Reprodutibilidade**: avaliação automática via gold set.
* **Modularidade**: checks independentes, facilmente adicionáveis.
* **Configuração**: perfis YAML por cliente/domínio.
* **Explainability**: alertas incluem evidência e sugestão.

---

## Roadmap (extensões futuras)

* Batch mode (upload CSV de segmentos e relatório agregado)
* Exportação de relatório (CSV/HTML/PDF)
* Check de placeholders (localização: `{name}`, `%s`, `\n`, etc.)
* Check terminológico (glossário por cliente/domínio)
* CLI estável para integração com pipelines de tradução

---

## Licença

Projeto académico (uso educacional). Ajustar conforme requisitos da unidade curricular/instituição.