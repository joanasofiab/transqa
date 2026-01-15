# TransQA — Quality Assurance (QA) para Tradução (EN/ES → PT)

TransQA é um protótipo de ferramenta de *Quality Assurance* para tradução, orientado a regras e configurável por cliente. O objetivo é detetar problemas frequentes em segmentos traduzidos (p.ex., números alterados, datas ambíguas, moedas/unidades omitidas, URLs/IDs não preservados), fornecendo alertas com evidências e sugestões de correção.

O projeto foi desenvolvido para ser utilizável, reprodutível e extensível, suportando perfis de configuração (por cliente/domínio) e avaliação automática com um conjunto “gold” de casos anotados.

---

## Funcionalidades principais

- **Checks implementados (rule-based)**
  - Dates (datas numéricas; deteção e aviso de ambiguidade)
  - Numbers (números gerais; com normalização PT/EN/ES e mitigação de falsos positivos em IDs)
  - Currencies (montantes monetários com símbolo e valor)
  - Percentages (percentagens com `%`)
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
  - geração de resultados e métricas em `eval/`

---

## Quickstart (correr localmente)

```powershell
git clone https://github.com/joanasofiab/transqa.git
cd transqa
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py

Abrir no browser: http://localhost:8501

Avaliação (gold set)

python -m eval.evaluate

Outputs gerados:

eval/eval_results.csv

eval/eval_summary.csv

eval/eval_summary.txt

Para correr avaliação com outro perfil:

$env:TRANSQA_CONFIG="config\client_demo.yaml"
python -m eval.evaluate

Estrutura do projeto (visão geral)

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
    punctuation.py
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
  reports/
    html_report.py
  requirements.txt
  requirements-lock.txt

Arquitetura (como o sistema funciona)

1. Configuração (YAML) define checks ativos e regras (p.ex., símbolos monetários, unidades, datas ambíguas).
2. Runner (core/runner.py) recebe source, target, pair e config, executa checks ativos e agrega alertas.
3. Checks (checks/*.py) devolvem uma lista de Alert (core/models.py) com:
  - severidade (Critical, Warning, Info)
  - nome do check
  - evidência no source/target
  - mensagem e sugestão
4. UI (app.py) apresenta os resultados em tabela.

Perfis de configuração (YAML)
- Checks ativos em checks.enabled
- Regras em rules.* (exemplos):
  -  warn_ambiguous_numeric_dates: true
  - currency_symbols: ["€", "$", "£"]
  - units: ["°C", "mg", "kg", "cm", "mm"]

Nota metodológica (avaliação)
As métricas em eval/ são calculadas a nível “case-level”: um check conta como detetado se pelo menos um alerta desse tipo for emitido no segmento.

Roadmap (extensões futuras)
- Batch mode (upload CSV de segmentos e relatório agregado)
- Exportação de relatório (CSV/HTML/PDF)
- Check de placeholders (ex.: {name}, %s, \n)
- Check terminológico (glossário por cliente/domínio)
- CLI estável para integração com pipelines de tradução

Licença
Projeto académico (uso educacional). Ajustar conforme requisitos da unidade curricular/instituição.