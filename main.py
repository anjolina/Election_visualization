import os
import pandas as pd
import tkinter as tk
from tkinter import ttk
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Load Data ────────────────────────────────────────────────────────────────
CSV_FILE = "nepal_election_results_2017_2022_2026.csv"

df = pd.read_csv(CSV_FILE)
df_2026 = df[df["election_year"] == 2026].copy()

# Remove "Others/Independents" rows with 0 seats for cleaner charts
df_2026_clean = df_2026[df_2026["total_seats"] > 0].copy()

# For line chart: exclude IND rows, keep real parties across years
MAIN_PARTIES = ["NC", "CPN-UML", "CPN-MC", "RSP", "RPP", "NCP"]
df_trend = df[df["party_abbr"].isin(MAIN_PARTIES)].copy()

# Party color palette (consistent across all charts)
PARTY_COLORS = {
    "RSP":     "#E63946",
    "NC":      "#2196F3",
    "CPN-UML": "#FF6F00",
    "CPN-MC":  "#B71C1C",
    "NCP":     "#880E4F",
    "RPP":     "#4CAF50",
    "SSP":     "#9C27B0",
    "IND":     "#90A4AE",
    "JSP":     "#00838F",
    "RJP-N":   "#F9A825",
    "FSFN":    "#558B2F",
    "NSP":     "#6D4C41",
    "NWPP":    "#37474F",
    "RJM":     "#00695C",
    "CPN-US":  "#AD1457",
    "JP":      "#1565C0",
    "LSP":     "#4E342E",
    "NUP":     "#00897B",
}

# ── Chart Builders ────────────────────────────────────────────────────────────

def build_pie_chart():
    """Pie chart: 2026 seat share by party."""
    fig = px.pie(
        df_2026_clean,
        values="total_seats",
        names="party_abbr",
        title="🗳️ Nepal 2026 Election — Seat Share by Party",
        color="party_abbr",
        color_discrete_map=PARTY_COLORS,
        hole=0.35,
    )
    fig.update_traces(
        textposition="outside",
        textinfo="label+percent+value",
        hovertemplate="<b>%{label}</b><br>Seats: %{value}<br>Share: %{percent}<extra></extra>",
        pull=[0.05 if abbr == "RSP" else 0 for abbr in df_2026_clean["party_abbr"]],
    )
    fig.update_layout(
        title_font_size=20,
        legend_title_text="Party",
        margin=dict(t=80, b=60, l=40, r=40),
        paper_bgcolor="#0D1117",
        plot_bgcolor="#0D1117",
        font=dict(color="#E6EDF3", family="Segoe UI, sans-serif"),
        title_font_color="#E6EDF3",
    )
    fig.show()


def build_bar_chart():
    """Grouped bar chart: 2026 FPTP vs PR vs Total seats."""
    df_melted = df_2026_clean.melt(
        id_vars=["party_abbr", "party_name"],
        value_vars=["fptp_seats", "pr_seats", "total_seats"],
        var_name="Seat Type",
        value_name="Seats",
    )
    df_melted["Seat Type"] = df_melted["Seat Type"].map({
        "fptp_seats":  "FPTP Seats",
        "pr_seats":    "PR Seats",
        "total_seats": "Total Seats",
    })

    # Sort by total seats descending
    order = df_2026_clean.sort_values("total_seats", ascending=False)["party_abbr"].tolist()

    fig = px.bar(
        df_melted,
        x="party_abbr",
        y="Seats",
        color="Seat Type",
        barmode="group",
        title="📊 Nepal 2026 Election — FPTP vs PR vs Total Seats",
        labels={"party_abbr": "Party", "Seats": "Number of Seats"},
        color_discrete_map={
            "FPTP Seats":  "#E63946",
            "PR Seats":    "#2196F3",
            "Total Seats": "#4CAF50",
        },
        category_orders={"party_abbr": order},
        text_auto=True,
    )
    fig.update_traces(
        textfont_size=11,
        hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y}<extra></extra>",
    )
    fig.update_layout(
        title_font_size=20,
        xaxis_title="Party",
        yaxis_title="Number of Seats",
        legend_title_text="Seat Type",
        margin=dict(t=80, b=60, l=60, r=40),
        paper_bgcolor="#0D1117",
        plot_bgcolor="#161B22",
        font=dict(color="#E6EDF3", family="Segoe UI, sans-serif"),
        title_font_color="#E6EDF3",
        xaxis=dict(gridcolor="#30363D"),
        yaxis=dict(gridcolor="#30363D"),
    )
    fig.show()


def build_line_chart():
    """Line chart: Total seats over 2017 → 2022 → 2026 for major parties."""
    # Fill missing years with 0 for parties that didn't exist in that election
    all_years = [2017, 2022, 2026]
    records = []
    for abbr in MAIN_PARTIES:
        party_df = df_trend[df_trend["party_abbr"] == abbr]
        name = party_df["party_name"].iloc[0] if not party_df.empty else abbr
        for yr in all_years:
            yr_row = party_df[party_df["election_year"] == yr]
            seats = int(yr_row["total_seats"].values[0]) if not yr_row.empty else 0
            records.append({"Year": yr, "party_abbr": abbr, "party_name": name, "total_seats": seats})

    df_line = pd.DataFrame(records)

    fig = px.line(
        df_line,
        x="Year",
        y="total_seats",
        color="party_abbr",
        markers=True,
        title="📈 Nepal Elections — Party Seat Trends (2017 → 2022 → 2026)",
        labels={"total_seats": "Total Seats Won", "party_abbr": "Party"},
        color_discrete_map=PARTY_COLORS,
        text="total_seats",
    )
    fig.update_traces(
        mode="lines+markers+text",
        textposition="top center",
        line=dict(width=2.5),
        marker=dict(size=9),
        hovertemplate="<b>%{fullData.name}</b><br>Year: %{x}<br>Seats: %{y}<extra></extra>",
    )
    fig.update_layout(
        title_font_size=20,
        xaxis=dict(
            tickvals=[2017, 2022, 2026],
            ticktext=["2017", "2022", "2026"],
            gridcolor="#30363D",
        ),
        yaxis=dict(gridcolor="#30363D"),
        margin=dict(t=80, b=60, l=60, r=40),
        paper_bgcolor="#0D1117",
        plot_bgcolor="#161B22",
        font=dict(color="#E6EDF3", family="Segoe UI, sans-serif"),
        title_font_color="#E6EDF3",
        legend_title_text="Party",
    )
    fig.show()


# ── Tkinter Dashboard ─────────────────────────────────────────────────────────

def launch_dashboard():
    root = tk.Tk()
    root.title("🗳️ Nepal Election Results Visualizer")
    root.geometry("520x420")
    root.resizable(False, False)
    root.configure(bg="#0D1117")

    # ── Styles
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background="#0D1117")
    style.configure(
        "TButton",
        font=("Segoe UI", 11, "bold"),
        padding=10,
        background="#21262D",
        foreground="#E6EDF3",
        borderwidth=0,
        relief="flat",
    )
    style.map("TButton",
              background=[("active", "#30363D"), ("pressed", "#388BFD")],
              foreground=[("active", "#FFFFFF")])

    # ── Header
    header = tk.Label(
        root,
        text="🇳🇵  Nepal Election Results Visualizer",
        font=("Segoe UI", 15, "bold"),
        bg="#0D1117",
        fg="#E6EDF3",
        pady=14,
    )
    header.pack(fill="x")

    sub = tk.Label(
        root,
        text="Elections: 2017  •  2022  •  2026",
        font=("Segoe UI", 10),
        bg="#0D1117",
        fg="#8B949E",
    )
    sub.pack()

    separator = tk.Frame(root, bg="#30363D", height=1)
    separator.pack(fill="x", padx=30, pady=12)

    # ── Summary stats (2026)
    stats_frame = tk.Frame(root, bg="#161B22", bd=0, relief="flat")
    stats_frame.pack(padx=30, pady=4, fill="x")

    stats = [
        ("RSP (Winner)", "182 seats", "#E63946"),
        ("NC (2nd)",     " 38 seats", "#2196F3"),
        ("CPN-UML (3rd)"," 25 seats", "#FF6F00"),
    ]
    for label, value, color in stats:
        row = tk.Frame(stats_frame, bg="#161B22")
        row.pack(fill="x", padx=12, pady=3)
        tk.Label(row, text=label, font=("Segoe UI", 10), bg="#161B22", fg="#8B949E", width=18, anchor="w").pack(side="left")
        tk.Label(row, text=value, font=("Segoe UI", 10, "bold"), bg="#161B22", fg=color).pack(side="left")

    separator2 = tk.Frame(root, bg="#30363D", height=1)
    separator2.pack(fill="x", padx=30, pady=12)

    # ── Buttons
    btn_frame = ttk.Frame(root)
    btn_frame.pack(pady=4)

    buttons = [
        ("🥧  Pie Chart  —  2026 Seat Share",     build_pie_chart),
        ("📊  Bar Chart  —  2026 FPTP vs PR",      build_bar_chart),
        ("📈  Line Chart — Trends 2017–2026",      build_line_chart),
    ]

    for text, cmd in buttons:
        btn = ttk.Button(btn_frame, text=text, command=cmd, width=42)
        btn.pack(pady=6)

    # ── Footer
    footer = tk.Label(
        root,
        text="Data sources: Election Commission of Nepal  |  Made with Plotly + Tkinter",
        font=("Segoe UI", 8),
        bg="#0D1117",
        fg="#484F58",
        pady=10,
    )
    footer.pack(side="bottom")

    root.mainloop()


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    launch_dashboard()
