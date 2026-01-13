import pandas as pd


def build_html_report(df: pd.DataFrame, title: str = "TransQA Report") -> str:
    if df.empty:
        return f"<html><head><meta charset='utf-8'><title>{title}</title></head><body><h1>{title}</h1><p>Sem alertas.</p></body></html>"

    summary = df["severity"].value_counts().to_dict()
    summary_html = "".join([f"<li><b>{k}</b>: {v}</li>" for k, v in summary.items()])

    table_html = df.to_html(index=False, escape=True)

    return f"""
    <html>
      <head>
        <meta charset="utf-8">
        <title>{title}</title>
        <style>
          body {{ font-family: Arial, sans-serif; margin: 24px; }}
          table {{ border-collapse: collapse; width: 100%; }}
          th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
          th {{ background: #f5f5f5; }}
        </style>
      </head>
      <body>
        <h1>{title}</h1>
        <h2>Resumo</h2>
        <ul>{summary_html}</ul>
        <h2>Detalhe</h2>
        {table_html}
      </body>
    </html>
    """