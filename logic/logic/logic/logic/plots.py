cat << 'EOF' > plots.py
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from config import HAMLET_BASELINE, SONNET_BASELINE, RICHARD_BASELINE

def build_sentiment_map(input_sentiment: dict, config: dict) -> go.Figure:
    fig = go.Figure()

    fig.add_shape(type="rect", x0=-1, x1=0, y0=0, y1=1, fillcolor="rgba(139,26,26,0.07)", line_width=0)
    fig.add_shape(type="rect", x0=0, x1=1, y0=0, y1=1, fillcolor="rgba(61,90,62,0.07)", line_width=0)
    fig.add_shape(type="rect", x0=-1, x1=0, y0=-1, y1=0, fillcolor="rgba(139,26,26,0.04)", line_width=0)
    fig.add_shape(type="rect", x0=0, x1=1, y0=-1, y1=0, fillcolor="rgba(61,90,62,0.04)", line_width=0)

    fig.add_hline(y=0.5, line_color="#3a2e1a", line_dash="dot", line_width=1)
    fig.add_vline(x=0,   line_color="#3a2e1a", line_dash="dot", line_width=1)

    baselines = []
    if config.get("show_hamlet", True): baselines.append(HAMLET_BASELINE)
    if config.get("show_sonnet", True): baselines.append(SONNET_BASELINE)
    if config.get("show_richard", True): baselines.append(RICHARD_BASELINE)

    for b in baselines:
        fig.add_trace(go.Scatter(
            x=[b["polarity"]], y=[b["subjectivity"]],
            mode="markers+text",
            marker=dict(size=14, color="#7a5c38", symbol="diamond", line=dict(color="#d4a843", width=1.5)),
            text=[b["label"]], textposition="top center",
            textfont=dict(color="#c9a96e", size=10, family="IM Fell English"),
            name=b["label"],
            hovertemplate=f"<b>{b['label']}</b><br>Polarity: {b['polarity']:.2f}<br>Subjectivity: {b['subjectivity']:.2f}<extra></extra>",
        ))

    fig.add_trace(go.Scatter(
        x=[input_sentiment["polarity"]], y=[input_sentiment["subjectivity"]],
        mode="markers+text",
        marker=dict(size=20, color="#d4a843", symbol="star", line=dict(color="#f5efe0", width=2)),
        text=["◀ Your Text"], textposition="middle right",
        textfont=dict(color="#f5efe0", size=12, family="Cinzel"),
        name="Your Text",
        hovertemplate="<b>Your Text</b><br>" + f"Polarity: {input_sentiment['polarity']:.3f}<br>" + f"Subjectivity: {input_sentiment['subjectivity']:.3f}<br>" + f"Archetype: {input_sentiment['archetype']}<extra></extra>",
    ))

    label_cfg = dict(font=dict(size=9, color="#5a4a2a", family="Cinzel"), showarrow=False)
    fig.add_annotation(x=-0.7, y=0.85, text="DARK · EMOTIONAL",  **label_cfg)
    fig.add_annotation(x= 0.7, y=0.85, text="LIGHT · EMOTIONAL", **label_cfg)
    fig.add_annotation(x=-0.7, y=0.15, text="DARK · REGAL",      **label_cfg)
    fig.add_annotation(x= 0.7, y=0.15, text="LIGHT · REGAL",     **label_cfg)

    fig.update_layout(
        paper_bgcolor="#110d07", plot_bgcolor="#130f05",
        font=dict(color="#c9a96e", family="Crimson Pro"),
        title=dict(text="SENTIMENT MAP — Shakespearean Corpus Comparison", font=dict(family="Cinzel", size=13, color="#d4a843"), x=0.5),
        xaxis=dict(title=dict(text="Polarity  ← Dark · · · Light →", font=dict(size=10, family="Cinzel")), range=[-1.05, 1.05], gridcolor="#1e1a10", zerolinecolor="#3a2e1a", tickfont=dict(size=9)),
        yaxis=dict(title=dict(text="Subjectivity  ← Regal · · · Emotional →", font=dict(size=10, family="Cinzel")), range=[-0.05, 1.05], gridcolor="#1e1a10", zerolinecolor="#3a2e1a", tickfont=dict(size=9)),
        legend=dict(bgcolor="#1e1608", bordercolor="#3a2e1a", borderwidth=1, font=dict(size=9, family="IM Fell English")),
        height=420, margin=dict(l=60, r=40, t=50, b=50),
    )
    return fig

def build_sentence_chart(sentences: list) -> go.Figure:
    if not sentences: return go.Figure()
    df = pd.DataFrame(sentences)
    df.index = [f"S{i+1}" for i in range(len(df))]
    colors = ["#7fc47f" if p > 0.1 else "#e06060" if p < -0.1 else "#d4a843" for p in df["polarity"]]

    fig = go.Figure(go.Bar(x=df.index, y=df["polarity"], marker_color=colors, marker_line_color="#3a2e1a", marker_line_width=1, hovertemplate="<b>%{x}</b><br>Polarity: %{y:.3f}<br><extra></extra>"))
    fig.update_layout(
        paper_bgcolor="#110d07", plot_bgcolor="#130f05",
        font=dict(color="#c9a96e", family="Crimson Pro"),
        title=dict(text="PER-SENTENCE POLARITY", font=dict(family="Cinzel", size=12, color="#d4a843"), x=0.5),
        xaxis=dict(gridcolor="#1e1a10", tickfont=dict(size=9)),
        yaxis=dict(gridcolor="#1e1a10", range=[-1.1, 1.1], title=dict(text="Polarity", font=dict(size=9, family="Cinzel"))),
        height=240, margin=dict(l=50, r=20, t=40, b=40), showlegend=False,
    )
    fig.add_hline(y=0, line_color="#5a4a2a", line_dash="dash", line_width=1)
    return fig

def build_radar_chart(sentiment: dict) -> go.Figure:
    categories = ["Regal Authority", "Emotional Depth", "Narrative Light", "Archaic Density", "Tragic Weight"]
    pol = sentiment["polarity"]
    values = [sentiment["authoritative_score"], sentiment["emotional_score"], max(0, pol * 100 + 50), min(100, sentiment.get("density", 0) * 20), max(0, -pol * 100 + 50)]
    values += [values[0]]
    categories_closed = categories + [categories[0]]

    fig = go.Figure(go.Scatterpolar(r=values, theta=categories_closed, fill='toself', fillcolor='rgba(212,168,67,0.15)', line=dict(color='#d4a843', width=2), marker=dict(color='#d4a843', size=6)))
    fig.update_layout(
        paper_bgcolor="#110d07",
        polar=dict(
            bgcolor="#130f05",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#2e2510", tickfont=dict(size=8, color="#7a5c38")),
            angularaxis=dict(gridcolor="#2e2510", tickfont=dict(size=9, color="#c9a96e", family="Cinzel")),
        ),
        title=dict(text="LITERARY PROFILE", font=dict(family="Cinzel", size=12, color="#d4a843"), x=0.5),
        height=300, margin=dict(l=40, r=40, t=50, b=20),
    )
    return fig
EOF