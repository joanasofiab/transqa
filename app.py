import yaml
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

    # ---- Inputs ----
    col1, col2 = st.columns(2)
    with col1:
        source = st.text_area("Texto original (Source)", height=260)
    with col2:
        target = st.text_area("Texto traduzido (Target)", height=260)

    # ---- Execução ----
    if st.button("Analisar"):
        alerts = run_all_checks(source, target, pair, config)
        df = alerts_to_dataframe(alerts)

        st.subheader("Resultados")

        if df.empty:
            st.success("Sem alertas detetados com as regras atuais.")
            return

        # ---- Filtros ----
        c1, c2 = st.columns([1, 2])

        with c1:
            severities = ["Critical", "Warning", "Info"]
            selected_sev = st.multiselect(
                "Filtrar severidade",
                severities,
                default=["Critical", "Warning", "Info"]
            )

        with c2:
            check_options = sorted(df["check"].unique().tolist())
            selected_checks = st.multiselect(
                "Filtrar tipo de check",
                check_options,
                default=check_options
            )

        df_view = df[df["severity"].isin(selected_sev) & df["check"].isin(selected_checks)].copy()

        # ---- Tabela ----
        st.dataframe(df_view, use_container_width=True)

        # ---- Resumo ----
        total = len(df_view)
        crit = int((df_view["severity"] == "Critical").sum())
        warn = int((df_view["severity"] == "Warning").sum())
        info = int((df_view["severity"] == "Info").sum())
        st.info(f"Alertas (filtrados): {total} | Critical={crit} | Warning={warn} | Info={info}")

        # ---- Export ----
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


if __name__ == "__main__":
    main()