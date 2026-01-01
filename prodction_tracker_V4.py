from dash import Dash, html, dcc, Input, Output, State, ctx,dash_table
import dash
# import dash_table
import plotly.express as px
import pandas as pd
from datetime import datetime
import pytz
import sqlite3

# ---------- DATABASE FUNCTIONS ----------
DB_FILE = "transactions.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        desc TEXT,
        type TEXT,
        amt REAL,
        date TEXT,
        time TEXT
    )
    """)
    conn.commit()
    conn.close()

def add_transaction(desc, type_, amt, date, time):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO transactions (desc, type, amt, date, time) VALUES (?, ?, ?, ?, ?)",
        (desc, type_, amt, date, time)
    )
    conn.commit()
    conn.close()

def update_transaction(row_id, desc, type_, amt):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "UPDATE transactions SET desc=?, type=?, amt=? WHERE id=?",
        (desc, type_, amt, row_id)
    )
    conn.commit()
    conn.close()

def delete_transaction(row_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM transactions WHERE id=?", (row_id,))
    conn.commit()
    conn.close()

def get_transactions():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    return df

# ---------- INITIALIZE DB ----------
init_db()

# ---------- DASH APP ----------
app = Dash(__name__)

server = app.server
app.title = "Expense Tracker"

# ---------- STYLES ----------
hidden_style = {"display": "none"}
visible_style = {"display": "block"}

# Responsive body & container
body_style = {
    "fontFamily": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    "backgroundColor": "#e8f0f8",
    "display": "flex",
    "justifyContent": "center",
    "alignItems": "flex-start",
    "minHeight": "100vh",
    "padding": "20px 10px",
}
container_style = {
    "background": "#ffffff",
    "padding": "25px",
    "borderRadius": "25px",
    "boxShadow": "0 15px 35px rgba(0,0,0,0.15)",
    "maxWidth": "950px",
    "width": "100%",
    "boxSizing": "border-box",
}

heading_style = {"textAlign": "center", "color": "#2c3e50", "marginBottom": "35px",
                 "fontSize": "48px", "fontWeight": "900", "letterSpacing": "1px"}

subtitle_row_style = {"display": "flex", "justifyContent": "space-between",
                      "alignItems": "center", "marginBottom": "15px"}

subtitle_style = {"textAlign": "center", "flex": "1", "fontSize": "30px",
                  "fontWeight": "bold", "color": "#2980b9", "textShadow": "1px 1px 2px #a3c4f0"}

toggle_button_style = {"background": "none", "border": "none", "cursor": "pointer",
                       "fontSize": "24px", "color": "#2980b9", "transition": "transform 0.3s ease"}

section_style = {"marginBottom": "30px",
                 "background": "linear-gradient(135deg, #d0e8ff, #a3c4f0)",
                 "padding": "25px", "borderRadius": "20px",
                 "boxShadow": "0 8px 25px rgba(0,0,0,0.12)",
                 "transition": "all 0.3s ease"}

# Responsive row
row_style = {"display": "flex", "flexWrap": "wrap", "gap": "10px",
             "alignItems": "center", "marginBottom": "12px", "width": "100%"}

input_style = {"flex": "1 1 150px", "padding": "12px", "border": "1px solid #ddd",
               "borderRadius": "12px", "fontSize": "16px", "minWidth": "120px"}

dropdown_style = {"flex": "1 1 130px", "minWidth": "120px"}

button_style = {"backgroundColor": "#2980b9", "color": "white", "border": "none",
                "padding": "14px 28px", "borderRadius": "12px", "cursor": "pointer",
                "fontSize": "18px", "fontWeight": "bold",
                "boxShadow": "0 6px 12px rgba(0,0,0,0.15)",
                "transition": "all 0.3s ease"}

summary_style = {"background": "linear-gradient(135deg, #6fb1fc, #3498db)", "padding": "20px",
                 "borderRadius": "20px", "textAlign": "center", "color": "#fff",
                 "marginTop": "20px", "boxShadow": "0 8px 25px rgba(0,0,0,0.12)",
                 "width": "100%", "boxSizing": "border-box"}

summary_text_style = {"fontSize": "18px", "margin": "6px 0", "fontWeight": "bold"}

# ---------- LAYOUT ----------
app.layout = html.Div(
    style=body_style,
    children=[
        html.Div(
            style=container_style,
            children=[
                html.H1("Expense Tracker", style=heading_style),

                # ---------- FILTERS ----------
                html.Div(
                    style=row_style,
                    children=[
                        dcc.Dropdown(
                            id="filter-cat",
                            options=[
                                {"label": "All Categories", "value": "All"},
                                {"label": "Housing", "value": "Housing"},
                                {"label": "Food", "value": "Food"},
                                {"label": "Transportation", "value": "Transportation"},
                                {"label": "Entertainment", "value": "Entertainment"},
                                {"label": "Others", "value": "Others"},
                                {"label": "Income", "value": "Income"},
                            ],
                            value="All",
                            style={"flex": "1 1 160px"},
                        ),
                        dcc.DatePickerRange(
                            id="filter-date",
                            display_format="YYYY-MM-DD",
                            start_date_placeholder_text="Start Date",
                            end_date_placeholder_text="End Date",
                            style={"flex": "1 1 160px"},
                        ),
                        html.Button(
                            "Clear Filters",
                            id="clear-filters",
                            n_clicks=0,
                            style=button_style,
                        ),
                    ],
                ),

                # ---------- INCOME ----------
                html.Div(
                    children=[
                        html.Div(
                            style=subtitle_row_style,
                            children=[
                                html.Span("Income", style=subtitle_style),
                                html.Button("▼", id="toggle-income", n_clicks=0, style=toggle_button_style),
                            ],
                        ),
                        html.Div(
                            id="income-section",
                            style=visible_style,
                            children=[
                                html.Div(
                                    style=row_style,
                                    children=[
                                        dcc.Input(id="income-desc", placeholder="Description", style=input_style),
                                        dcc.Input(id="income-amt", placeholder="Amount (₹)", type="number", style=input_style),
                                        html.Button("Add", id="add-income", n_clicks=0, style=button_style),
                                    ],
                                ),
                            ],
                        ),
                    ],
                    style=section_style,
                ),

                # ---------- EXPENSE ----------
                html.Div(
                    children=[
                        html.Div(
                            style=subtitle_row_style,
                            children=[
                                html.Span("Expenses", style=subtitle_style),
                                html.Button("▼", id="toggle-expense", n_clicks=0, style=toggle_button_style),
                            ],
                        ),
                        html.Div(
                            id="expense-section",
                            style=visible_style,
                            children=[
                                html.Div(
                                    style=row_style,
                                    children=[
                                        dcc.Input(id="expense-desc", placeholder="Description", style=input_style),
                                        dcc.Dropdown(
                                            id="expense-cat",
                                            options=[
                                                {"label": "Housing", "value": "Housing"},
                                                {"label": "Food", "value": "Food"},
                                                {"label": "Transportation", "value": "Transportation"},
                                                {"label": "Entertainment", "value": "Entertainment"},
                                                {"label": "Others", "value": "Others"},
                                            ],
                                            placeholder="Category",
                                            style=dropdown_style,
                                        ),
                                        dcc.Input(id="expense-amt", placeholder="Amount (₹)", type="number", style=input_style),
                                        html.Button("Add", id="add-expense", n_clicks=0, style=button_style),
                                    ],
                                ),
                            ],
                        ),
                    ],
                    style=section_style,
                ),

                # ---------- BUDGET SUMMARY ----------
                html.Div(
                    children=[
                        html.H2("Budget Summary", style={"fontSize": "28px", "color": "#fff", "marginBottom": "20px"}),
                        html.P(["Total Income: ₹", html.Span("0", id="total-income")], style=summary_text_style),
                        html.P(["Total Expenses: ₹", html.Span("0", id="total-expenses")], style=summary_text_style),
                        html.P(["Balance: ₹", html.Span("0", id="balance")], style=summary_text_style),
                    ],
                    style=summary_style,
                ),

                # ---------- TRANSACTION HISTORY ----------
                dash_table.DataTable(
                    id="transaction-table",
                    columns=[
                        {"name": "ID", "id": "id", "hideable": True},
                        {"name": "Description", "id": "desc"},
                        {"name": "Category/Type", "id": "type"},
                        {"name": "Amount (₹)", "id": "amt"},
                        {"name": "Date", "id": "date"},
                        {"name": "Time", "id": "time"},
                    ],
                    data=[],
                    style_table={"marginTop": "20px", "width": "100%", "overflowX": "auto"},
                    style_header={"backgroundColor": "#2980b9","color": "white","fontWeight": "bold","fontSize": "14px"},
                    style_cell={"textAlign": "center","padding": "6px","fontSize": "12px", "minWidth": "80px"},
                    row_deletable=True,
                    editable=True,
                    style_data_conditional=[{"if": {"row_index": "odd"}, "backgroundColor": "#d0e8ff"}],
                ),

                # ---------- DOWNLOAD ----------
                html.Div(
                    style={"marginTop": "20px", "textAlign": "center"},
                    children=[
                        html.Button("Download CSV", id="download-csv", n_clicks=0, style=button_style),
                        dcc.Download(id="download-data"),
                    ],
                ),

                # ---------- PIE CHART ----------
                html.Div(dcc.Graph(id="expense-pie-chart", style={"width": "100%", "height": "auto"}), style={"marginTop": "20px", "width": "100%"}),
            ],
        )
    ],
)

# ---------- MAIN CALLBACK ----------
@app.callback(
    Output("transaction-table", "data"),
    Output("total-income", "children"),
    Output("total-expenses", "children"),
    Output("balance", "children"),
    Output("expense-pie-chart", "figure"),
    Output("income-desc", "value"),
    Output("income-amt", "value"),
    Output("expense-desc", "value"),
    Output("expense-cat", "value"),
    Output("expense-amt", "value"),
    Output("filter-cat", "value"),
    Output("filter-date", "start_date"),
    Output("filter-date", "end_date"),
    Input("add-income", "n_clicks"),
    Input("add-expense", "n_clicks"),
    Input("filter-cat", "value"),
    Input("filter-date", "start_date"),
    Input("filter-date", "end_date"),
    Input("transaction-table", "data_timestamp"),
    Input("clear-filters", "n_clicks"),
    State("income-desc", "value"),
    State("income-amt", "value"),
    State("expense-desc", "value"),
    State("expense-cat", "value"),
    State("expense-amt", "value"),
    State("transaction-table", "data"),
    State("transaction-table", "data_previous"),
)
def update_all(add_income, add_expense, category, start_date, end_date, ts, clear_clicks,
               inc_desc, inc_amt, exp_desc, exp_cat, exp_amt,
               current_data, previous_data):

    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    triggered = ctx.triggered_id

    # ---------- CLEAR FILTERS ----------
    if triggered == "clear-filters":
        category = "All"
        start_date = None
        end_date = None

    # ---------- ADD ----------
    if triggered == "add-income" and inc_amt:
        add_transaction(inc_desc or "Income", "Income", float(inc_amt), date_str, time_str)

    if triggered == "add-expense" and exp_amt:
        add_transaction(exp_desc or "Expense", exp_cat or "Others", float(exp_amt), date_str, time_str)

    # ---------- EDIT / DELETE ----------
    if triggered == "transaction-table" and previous_data:
        prev_ids = {r["id"] for r in previous_data}
        curr_ids = {r["id"] for r in current_data}

        # Deleted rows
        for del_id in prev_ids - curr_ids:
            delete_transaction(del_id)

        # Edited rows
        for r in current_data:
            p = next((x for x in previous_data if x["id"] == r["id"]), None)
            if p and (p["desc"] != r["desc"] or p["type"] != r["type"] or p["amt"] != r["amt"]):
                update_transaction(r["id"], r["desc"], r["type"], r["amt"])

    # ---------- READ FROM DB ----------
    df = get_transactions()

    # ---------- APPLY FILTERS (SINGLE SOURCE) ----------
    filtered_df = df.copy()

    if category and category != "All":
        filtered_df = filtered_df[filtered_df["type"] == category]

    if start_date:
        filtered_df = filtered_df[filtered_df["date"] >= start_date]

    if end_date:
        filtered_df = filtered_df[filtered_df["date"] <= end_date]

    # ---------- SUMMARY (FILTERED) ----------
    total_income = filtered_df[filtered_df["type"] == "Income"]["amt"].sum() if not filtered_df.empty else 0
    total_expenses = filtered_df[filtered_df["type"] != "Income"]["amt"].sum() if not filtered_df.empty else 0
    balance = total_income - total_expenses

    # ---------- PIE CHART (FILTERED) ----------
    pie_df = filtered_df[filtered_df["type"] != "Income"]
    fig = px.pie(
        pie_df,
        names="type",
        values="amt",
        title="Expenses by Category"
    ) if not pie_df.empty else px.pie()

    # ---------- CLEAR INPUTS ----------
    return (
        filtered_df.to_dict("records"),
        str(total_income),
        str(total_expenses),
        str(balance),
        fig,
        "", None, "", None, None,
        category,
        start_date,
        end_date
    )

# ---------- DOWNLOAD ----------
@app.callback(
    Output("download-data", "data"),
    Input("download-csv", "n_clicks"),
    prevent_initial_call=True,
)
def download_csv(n):
    df = get_transactions()
    return dcc.send_data_frame(df.to_csv, "transactions.csv", index=False)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=443,debug=False)
