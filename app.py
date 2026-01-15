import io
import yaml
import pandas as pd
import streamlit as st

from core.runner import run_all_checks, alerts_to_dataframe
from reports.html_report import build_html_report


def load_config(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    st.set_page_config(page_title="TransQA", layout="wide")

    # ---- Seleção de perfil (YAML) ----
    profile_map = {
        "Default": "config/default.yaml",
        "Client Demo": "config/client_demo.yaml",
    }

    profile_label = st.sidebar.selectbox("Perfil", list(profile_map.keys()), index=0)
    config_path = profile_map[profile_label]
    config = load_config(config_path)

    title = config.get("app", {}).get("title", "TransQA")
    st.title(title)
    st.caption(f"Perfil ativo: {profile_label} ({config_path})")

    # ---- Par linguístico (MVP) ----
    default_pair = config.get("app", {}).get("default_pair", "EN->PT")
    pair_options = ["EN->PT", "ES->PT"]
    pair_index = pair_options.index(default_pair) if default_pair in pair_options else 0
    pair = st.selectbox("Par linguístico", pair_options, index=pair_index)

    # ---- Tabs: Single / Batch ----
    tab_single, tab_batch = st.tabs(["Análise (1 segmento)", "Batch mode (CSV)"])

    # =========================
    # TAB 1 — Single segment
    # =========================
    with tab_single:
        col1, col2 = st.columns(2)
        with col1:
            source = st.text_area("Texto original (Source)", height=260, key="single_source")
        with col2:
            target = st.text_area("Texto traduzido (Target)", height=260, key="single_target")

        if st.button("Analisar", key="single_analyze"):
            alerts = run_all_checks(source, target, pair, config)
            df = alerts_to_dataframe(alerts)

            st.subheader("Resultados")

            if df.empty:
                st.success("Sem alertas detetados com as regras atuais.")
            else:
                # ---- Filtros ----
                c1, c2 = st.columns([1, 2])

                with c1:
                    severities = ["Critical", "Warning", "Info"]
                    selected_sev = st.multiselect(
                        "Filtrar severidade",
                        severities,
                        default=severities,
                        key="single_sev"
                    )

                with c2:
                    check_options = sorted(df["check"].unique().tolist())
                    selected_checks = st.multiselect(
                        "Filtrar tipo de check",
                        check_options,
                        default=check_options,
                        key="single_checks"
                    )

                df_view = df[df["severity"].isin(selected_sev) & df["check"].isin(selected_checks)].copy()

                # ---- KPIs ----
                total = len(df_view)
                crit = int((df_view["severity"] == "Critical").sum())
                warn = int((df_view["severity"] == "Warning").sum())
                info_ = int((df_view["severity"] == "Info").sum())

                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Alertas", total)
                k2.metric("Critical", crit)
                k3.metric("Warning", warn)
                k4.metric("Info", info_)

                # ---- Tabela ----
                st.dataframe(df_view, width="stretch", hide_index=True)

                # ---- Export (CSV + HTML) ----
                st.download_button(
                    label="Exportar CSV",
                    data=df_view.to_csv(index=False).encode("utf-8"),
                    file_name="transqa_report.csv",
                    mime="text/csv"
                )

                html = build_html_report(df_view, title=f"TransQA Report ({pair}) — {profile_label}")
                st.download_button(
                    label="Exportar HTML",
                    data=html.encode("utf-8"),
                    file_name="transqa_report.html",
                    mime="text/html"
                )

    # =========================
    # TAB 2 — Batch mode (CSV)
    # =========================
    with tab_batch:
        st.write("CSV esperado: colunas **source**, **target** e opcionalmente **pair** (EN->PT / ES->PT).")

        uploaded = st.file_uploader("Carregar CSV", type=["csv"], key="batch_uploader")

        if uploaded is not None:
            try:
                content = uploaded.getvalue()

                try:
                    batch_df = pd.read_csv(io.BytesIO(content), encoding="utf-8")
                except UnicodeDecodeError:
                    batch_df = pd.read_csv(io.BytesIO(content), encoding="latin-1")

                batch_df.columns = [c.strip() for c in batch_df.columns]

                required = {"source", "target"}
                missing = required - set(batch_df.columns)
                if missing:
                    st.error(f"Faltam colunas obrigatórias: {', '.join(sorted(missing))}")
                    return

                has_pair = "pair" in batch_df.columns

                max_rows_default = min(len(batch_df), 200)
                cA, cB, cC = st.columns([1, 1, 2])

                with cA:
                    limit_rows = st.number_input(
                        "Máx. linhas a processar",
                        min_value=1,
                        max_value=max(1, len(batch_df)),
                        value=max_rows_default,
                        step=1,
                        key="batch_limit"
                    )

                with cB:
                    stop_on_empty = st.checkbox("Ignorar linhas vazias", value=True, key="batch_ignore_empty")

                with cC:
                    st.caption("Dica: começa com 20–50 linhas para testar, depois aumenta.")

                if st.button("Analisar CSV (Batch)", key="batch_analyze"):
                    to_process = batch_df.head(int(limit_rows)).copy()

                    all_alerts_rows = []
                    per_row_summary = []

                    progress = st.progress(0)
                    status = st.empty()

                    n = len(to_process)

                    # Atenção: o index do DataFrame pode não ser 0..N-1
                    # Vamos usar row_id sequencial (1..n) para ficar limpo
                    for idx, (_, row) in enumerate(to_process.iterrows(), start=1):
                        src = "" if pd.isna(row["source"]) else str(row["source"])
                        tgt = "" if pd.isna(row["target"]) else str(row["target"])

                        row_pair = pair
                        if has_pair and not pd.isna(row["pair"]):
                            row_pair = str(row["pair"]).strip()

                        if stop_on_empty and (not src.strip() and not tgt.strip()):
                            per_row_summary.append({
                                "row_id": idx,
                                "pair": row_pair,
                                "n_alerts": 0,
                                "critical": 0,
                                "warning": 0,
                                "info": 0,
                            })
                        else:
                            alerts = run_all_checks(src, tgt, row_pair, config)
                            df_row = alerts_to_dataframe(alerts)

                            if df_row.empty:
                                per_row_summary.append({
                                    "row_id": idx,
                                    "pair": row_pair,
                                    "n_alerts": 0,
                                    "critical": 0,
                                    "warning": 0,
                                    "info": 0,
                                })
                            else:
                                crit = int((df_row["severity"] == "Critical").sum())
                                warn = int((df_row["severity"] == "Warning").sum())
                                info_ = int((df_row["severity"] == "Info").sum())

                                per_row_summary.append({
                                    "row_id": idx,
                                    "pair": row_pair,
                                    "n_alerts": int(len(df_row)),
                                    "critical": crit,
                                    "warning": warn,
                                    "info": info_,
                                })

                                df_row.insert(0, "row_id", idx)
                                df_row.insert(1, "pair", row_pair)
                                all_alerts_rows.append(df_row)

                        progress.progress(min(1.0, idx / max(1, n)))
                        status.write(f"A processar linha {idx}/{n}...")

                    progress.progress(1.0)
                    status.write("Batch concluído.")

                    summary_df = pd.DataFrame(per_row_summary)

                    if all_alerts_rows:
                        alerts_df = pd.concat(all_alerts_rows, ignore_index=True)
                    else:
                        alerts_df = pd.DataFrame(columns=[
                            "row_id", "pair", "severity", "check",
                            "source_evidence", "target_evidence", "message", "suggestion"
                        ])

                    st.markdown("### Resumo (por linha)")
                    st.dataframe(summary_df, width="stretch", hide_index=True)

                    st.markdown("### Alertas (detalhe)")
                    st.dataframe(alerts_df, width="stretch", hide_index=True)

                    st.download_button(
                        label="Exportar resumo CSV",
                        data=summary_df.to_csv(index=False).encode("utf-8"),
                        file_name="transqa_batch_summary.csv",
                        mime="text/csv"
                    )

                    st.download_button(
                        label="Exportar alertas CSV",
                        data=alerts_df.to_csv(index=False).encode("utf-8"),
                        file_name="transqa_batch_alerts.csv",
                        mime="text/csv"
                    )

                    html = build_html_report(alerts_df, title=f"TransQA Batch Report — {profile_label}")
                    st.download_button(
                        label="Exportar alertas HTML",
                        data=html.encode("utf-8"),
                        file_name="transqa_batch_alerts.html",
                        mime="text/html"
                    )

            except Exception as e:
                st.error(f"Erro ao ler/processar o CSV: {e}")


if __name__ == "__main__":
    main()