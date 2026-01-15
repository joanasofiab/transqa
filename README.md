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
  - geração de resultados (`eval/eval_results.csv`) e métricas (`eval/eval_summary.txt`)

## Escopo e não-escopo

**Dentro do escopo**
- QA baseada em regras (regex + normalização) para fenómenos objetivos: números, datas, moedas, unidades, intervalos e itens “não traduzíveis”.
- Configuração por perfil de cliente/domínio.
- Avaliação reprodutível via conjunto de testes anotado.

**Fora do escopo (por desenho)**
- Avaliação semântica profunda (p.ex., “tradução correta” a nível de sentido)
- Ajustes automáticos ao texto alvo (o sistema apenas sinaliza)
- Integração direta com CAT tools (pode ser adicionada futuramente via CLI/API)

## Requisitos

- Python 3.10+ (recomendado)

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

- eval/eval_results.csv

- eval/eval_summary.csv

- eval/eval_summary.txt

Para correr a avaliação com outro perfil:
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

Arquitetura (como o sistema funciona)

- Configuração (YAML) define quais os checks ativos e algumas regras (p.ex., símbolos monetários, unidades, datas ambíguas).

- Runner (core/runner.py) recebe source, target, pair e config, executa os checks ativados e agrega alertas.

- Checks (checks/*.py) devolvem uma lista de Alert (modelo em core/models.py) com:

  - severidade (Critical, Warning, Info)

  - nome do check

  - evidência no source/target

  - mensagem e sugestão

  - UI (app.py) apresenta os resultados em tabela.

Perfis de configuração (YAML)

Exemplo: config/default.yaml (padrão)

  - checks ativos em checks.enabled

  - regras opcionais em rules.*, por exemplo:

  - warn_ambiguous_numeric_dates: true

  - currency_symbols: ["€", "$", "£"]

  - units: ["°C", "mg", "kg", "cm", "mm"]

Roadmap (extensões futuras)

- Batch mode (upload CSV de segmentos e relatório agregado)

- Exportação de relatório (CSV/HTML/PDF)

- Check de placeholders (ex.: {name}, %s, \n, etc.)

- Check terminológico (glossário por cliente/domínio)

- CLI estável para integração com pipelines de tradução

Licença

Projeto académico (uso educacional). Ajustar conforme requisitos da unidade curricular/instituição.
