import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Smart Expense Analyzer",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp                   { background-color: #0e1117; }
    .block-container         { padding: 2rem 2.5rem 3rem !important; max-width: 1300px; }

    .app-title { font-size:1.75rem; font-weight:800; color:#fafafa; margin:0; }
    .app-sub   { font-size:0.88rem; color:#8b90a7; margin:2px 0 22px; }

    .card {
        background: #1e2130;
        border-radius: 14px;
        padding: 20px 24px;
        border: 1px solid #2d3148;
        margin-bottom: 18px;
    }
    .card-title { font-size:0.72rem; font-weight:600; text-transform:uppercase;
                  letter-spacing:0.08em; color:#8b90a7; margin:0 0 8px; }
    .card-value { font-size:1.9rem; font-weight:800; color:#fafafa;
                  margin:0; line-height:1.2; }
    .card-sub   { font-size:0.78rem; color:#8b90a7; margin:4px 0 0; }

    .sec-label {
        font-size:0.95rem; font-weight:700; color:#fafafa;
        margin: 6px 0 14px;
        padding-left: 10px;
        border-left: 3px solid #4c8bf5;
    }

    .up-title { font-size:0.92rem; font-weight:600; color:#fafafa; margin:0 0 12px; }

    div[data-testid="stFileUploader"] {
        background: #151821;
        border-radius: 10px;
        border: 2px dashed #2d3148;
        padding: 6px 12px;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #4c8bf5;
        background: #1a1f32;
    }
    div[data-testid="stFileUploader"] label { color: #8b90a7 !important; }

    /* ── Transaction table HTML ── */
    .tx-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.875rem;
    }
    .tx-table thead tr {
        border-bottom: 1px solid #2d3148;
    }
    .tx-table thead th {
        text-align: left;
        padding: 10px 14px;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #8b90a7;
    }
    .tx-table tbody tr {
        border-bottom: 1px solid #252838;
        transition: background 0.15s;
    }
    .tx-table tbody tr:last-child { border-bottom: none; }
    .tx-table tbody tr:hover { background: #252b3b; }
    .tx-table tbody td {
        padding: 11px 14px;
        color: #fafafa;
        vertical-align: middle;
    }
    .tx-date { color: #8b90a7 !important; font-size:0.82rem !important; }
    .tx-desc { font-weight: 500; }

    /* ── Controls row ── */
    .stTextInput > div > div > input {
        background: #151821 !important;
        border: 1px solid #2d3148 !important;
        border-radius: 8px !important;
        color: #fafafa !important;
        font-size: 0.85rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #4c8bf5 !important;
        box-shadow: 0 0 0 2px rgba(76,139,245,0.15) !important;
    }
    .stSelectbox > div > div {
        background: #151821 !important;
        border: 1px solid #2d3148 !important;
        border-radius: 8px !important;
        color: #fafafa !important;
    }
    .tx-count {
        font-size: 0.78rem;
        color: #8b90a7;
        margin: 0 0 12px;
    }

    ::-webkit-scrollbar       { width:6px; height:6px; }
    ::-webkit-scrollbar-track { background:#0e1117; }
    ::-webkit-scrollbar-thumb { background:#2d3148; border-radius:4px; }
</style>
""", unsafe_allow_html=True)


# ── Category palette ────────────────────────────────────────────────────────
PALETTE = {
    "Food":              "#4c8bf5",
    "Travel":            "#34a853",
    "Shopping":          "#ff6d00",
    "Bills":             "#ea4335",
    "Entertainment":     "#ab47bc",
    "Health":            "#00bcd4",
    "Education":         "#ffb300",
    "Personal Transfer": "#546e7a",
    "Other":             "#78909c",
}

def cat_color(c):
    return PALETTE.get(c, "#78909c")

DARK_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#fafafa"),
)
GRID_COLOR = "#2d3148"
TICK_COLOR = "#8b90a7"


# ── Rule-based categorizer ──────────────────────────────────────────────────
RULES = [
    (["swiggy", "zomato", "dominos", "mcdonald", "kfc", "pizza", "burger",
       "dunzo", "blinkit", "instamart", "bigbasket"],          "Food"),
    (["uber", "ola", "rapido", "redbus", "irctc", "makemytrip",
       "goibibo", "yatra", "bus", "train", "flight", "metro"],  "Travel"),
    (["amazon", "flipkart", "myntra", "ajio", "meesho", "snapdeal",
       "nykaa", "tata cliq", "shopsy"],                         "Shopping"),
    (["netflix", "spotify", "prime video", "hotstar", "disney",
       "youtube premium", "zee5", "sonyliv", "apple music"],    "Entertainment"),
    (["apollo", "medplus", "1mg", "netmeds", "pharmeasy",
       "practo", "hospital", "clinic", "doctor", "pharmacy"],   "Health"),
    (["electricity", "water bill", "gas bill", "broadband",
       "jio", "airtel", "bsnl", "vi ", "vodafone", "postpaid",
       "prepaid", "recharge", "insurance", "lic ", "rent"],     "Bills"),
    (["school", "college", "university", "udemy", "coursera",
       "byju", "unacademy", "tuition", "fees"],                 "Education"),
    (["upi to", "imps to", "neft to", "transfer to",
       "sent to", "paid to"],                                   "Personal Transfer"),
]

def categorize(description: str) -> str:
    desc_lower = description.lower()
    for keywords, category in RULES:
        if any(kw in desc_lower for kw in keywords):
            return category
    return "Other"


# ── Recurring Expense Detector ──────────────────────────────────────────────
def detect_recurring(df):
    """
    Detect recurring expenses by analyzing transaction patterns.
    Identifies subscriptions, bills, and regular payments.
    """
    recurring = []
    
    # Group by description to find repeated transactions
    desc_groups = df.groupby("Description").agg({
        "Amount": ["count", "mean", "std"],
        "Date": ['min', 'max']
    }).reset_index()
    
    desc_groups.columns = ['Description', 'count', 'avg_amount', 'std_amount', 'first_date', 'last_date']
    
    for _, row in desc_groups.iterrows():
        desc = row['Description']
        count = row['count']
        avg_amt = abs(row['avg_amount'])
        first_date = row['first_date']
        last_date = row['last_date']
        
        # Detect patterns
        days_span = (last_date - first_date).days
        
        # Pattern: appears 2+ times with consistent amount (std < 10% of mean)
        is_consistent = row['std_amount'] is pd.isna(row['std_amount']) or (row['std_amount'] / avg_amt < 0.1) if avg_amt > 0 else False
        
        if count >= 2 and is_consistent is not False:
            # Infer frequency
            if count == 2 and days_span >= 25 and days_span <= 35:
                frequency = "Monthly"
                annual = avg_amt * 12
            elif count == 3 and days_span >= 14 and days_span <= 35:
                frequency = "Bi-weekly"
                annual = avg_amt * 26
            elif count >= 2 and days_span >= 6 and days_span <= 10:
                frequency = "Weekly"
                annual = avg_amt * 52
            elif count >= 4:
                frequency = "Monthly"
                annual = avg_amt * 12
            else:
                continue
            
            # Identify subscription keywords
            desc_lower = desc.lower()
            is_subscription = any(kw in desc_lower for kw in [
                'subscription', 'premium', 'netflix', 'spotify', 'prime', 
                'bill', 'electricity', 'water', 'gas', 'rent', 'insurance',
                'membership', 'fee', 'charges', 'auto-pay', 'recurring'
            ])
            
            recurring.append({
                'Description': desc,
                'Amount': avg_amt,
                'Count': count,
                'Frequency': frequency,
                'Annual': annual,
                'First_Date': first_date,
                'Last_Date': last_date,
                'IsSubscription': is_subscription
            })
    
    if recurring:
        recurring_df = pd.DataFrame(recurring).sort_values('Annual', ascending=False)
        return recurring_df
    return pd.DataFrame()


# ── Page header ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:10px;margin-bottom:2px;">
    <span style="font-size:1.8rem;">💰</span>
    <p class="app-title">Smart Expense Analyzer</p>
</div>
<p class="app-sub">Analyze your expenses automatically using AI</p>
""", unsafe_allow_html=True)

# ── Upload ───────────────────────────────────────────────────────────────────
st.markdown('<div class="card"><p class="up-title">📂 Upload your transaction CSV</p>',
            unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["csv"], label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        if not all(c in df.columns for c in ["Date", "Description", "Amount"]):
            st.error("CSV must contain: Date, Description, Amount")
            st.stop()

        df["Date"]     = pd.to_datetime(df["Date"])
        df["Amount"]   = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)

        # ── Apply rule-based categorization ──────────────────────────────────
        df["Category"] = df["Description"].apply(categorize)

        total_expense = abs(df["Amount"].sum())
        n             = len(df)
        avg_tx        = total_expense / n if n else 0
        cat_sum       = df.groupby("Category")["Amount"].sum().abs().sort_values(ascending=False)
        top_cat       = cat_sum.idxmax()
        top_amt       = int(cat_sum[top_cat])

        df["MonthNum"] = df["Date"].dt.month
        df["Month"]    = df["Date"].dt.strftime("%b")
        monthly = (df.groupby(["MonthNum", "Month"])["Amount"]
                     .sum().abs().reset_index()
                     .sort_values("MonthNum"))

        # ── KPI cards ────────────────────────────────────────────────────────
        st.markdown('<p class="sec-label">📊 Overview</p>', unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)

        k1.markdown(f"""<div class="card">
            <p class="card-title">Total Expenses</p>
            <p class="card-value">₹{int(total_expense):,}</p>
            <p class="card-sub">{n} transactions</p>
        </div>""", unsafe_allow_html=True)

        k2.markdown(f"""<div class="card">
            <p class="card-title">Avg per Transaction</p>
            <p class="card-value">₹{int(avg_tx):,}</p>
            <p class="card-sub">across all categories</p>
        </div>""", unsafe_allow_html=True)

        k3.markdown(f"""<div class="card">
            <p class="card-title">Top Category</p>
            <p class="card-value" style="color:{cat_color(top_cat)};">{top_cat}</p>
            <p class="card-sub">₹{top_amt:,} spent</p>
        </div>""", unsafe_allow_html=True)

        k4.markdown(f"""<div class="card">
            <p class="card-title">Categories</p>
            <p class="card-value">{len(cat_sum)}</p>
            <p class="card-sub">unique spend types</p>
        </div>""", unsafe_allow_html=True)

        # ════════════════════════════════════════════════════════════════════
        #  TRANSACTIONS TABLE
        # ════════════════════════════════════════════════════════════════════
        st.markdown('<p class="sec-label">🗒️ Transactions</p>', unsafe_allow_html=True)

        fc1, fc2, fc3 = st.columns([2, 1.2, 0.8])
        with fc1:
            search_q = st.text_input("", placeholder="🔍  Search description…",
                                     label_visibility="collapsed")
        with fc2:
            all_cats   = ["All Categories"] + sorted(df["Category"].unique().tolist())
            cat_filter = st.selectbox("", all_cats, label_visibility="collapsed")
        with fc3:
            sort_by = st.selectbox("", ["Date ↓", "Date ↑", "Amount ↓", "Amount ↑"],
                                   label_visibility="collapsed")

        # Apply filters
        filtered = df.copy()
        if search_q:
            filtered = filtered[
                filtered["Description"].str.contains(search_q, case=False, na=False)
            ]
        if cat_filter != "All Categories":
            filtered = filtered[filtered["Category"] == cat_filter]

        sort_map = {
            "Date ↓":   ("Date",   False),
            "Date ↑":   ("Date",   True),
            "Amount ↓": ("Amount", True),
            "Amount ↑": ("Amount", False),
        }
        sort_col, sort_asc = sort_map[sort_by]
        filtered = filtered.sort_values(sort_col, ascending=sort_asc)

        # Build HTML table
        def build_table(data):
            rows = ""
            for _, row in data.iterrows():
                date_str = row["Date"].strftime("%Y-%m-%d")
                desc     = row["Description"]
                amt      = row["Amount"]
                cat      = row["Category"]
                amt_str  = f"−₹{abs(int(amt)):,}" if amt < 0 else f"₹{int(amt):,}"

                rows += f"""
                <tr>
                    <td class="tx-date">{date_str}</td>
                    <td class="tx-desc">{desc}</td>
                    <td>{amt_str}</td>
                    <td>{cat}</td>
                </tr>"""

            return f"""
            <table class="tx-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Description</th>
                        <th>Amount</th>
                        <th>Category</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>"""

        st.markdown('<div class="card" style="padding:14px 18px;">', unsafe_allow_html=True)
        st.markdown(
            f'<p class="tx-count">Showing <strong style="color:#fafafa">'
            f'{len(filtered)}</strong> of {n} transactions</p>',
            unsafe_allow_html=True
        )
        table_html = build_table(filtered)
        scroll_h   = min(360, max(120, len(filtered) * 46 + 50))
        st.markdown(
            f'<div style="overflow-y:auto;max-height:{scroll_h}px;">{table_html}</div>',
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Insights ─────────────────────────────────────────────────────────
        st.markdown('<p class="sec-label">📈 Spending Insights</p>', unsafe_allow_html=True)
        col_pie, col_bar = st.columns([1, 1.15])

        with col_pie:
            pie_colors = [cat_color(c) for c in cat_sum.index]
            fig_pie = go.Figure(go.Pie(
                labels=cat_sum.index,
                values=cat_sum.values,
                hole=0.54,
                marker=dict(colors=pie_colors, line=dict(color="#0e1117", width=3)),
                textinfo="percent",
                textfont=dict(size=12, color="white", family="Inter"),
                hovertemplate="<b>%{label}</b><br>₹%{value:,}  (%{percent})<extra></extra>",
                insidetextorientation="radial",
            ))
            fig_pie.add_annotation(
                text=f"<b>₹{int(total_expense/1000)}K</b><br>"
                     f"<span style='font-size:11px'>Total</span>",
                x=0.5, y=0.5,
                font=dict(size=15, color="#fafafa", family="Inter"),
                showarrow=False, align="center",
            )
            fig_pie.update_layout(
                **DARK_LAYOUT,
                title=dict(text="Spending by Category",
                           font=dict(size=13, color="#fafafa"), x=0, xanchor="left"),
                margin=dict(t=40, b=10, l=10, r=130),
                legend=dict(orientation="v", x=1.0, y=0.5, xanchor="left",
                            yanchor="middle", font=dict(size=12, color="#fafafa"),
                            bgcolor="rgba(0,0,0,0)", itemsizing="constant"),
                height=320,
            )
            st.markdown('<div class="card" style="padding:14px 18px;">', unsafe_allow_html=True)
            st.plotly_chart(fig_pie, use_container_width=True,
                            config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

        with col_bar:
            cat_df = cat_sum.reset_index()
            cat_df.columns = ["Category", "Amount"]
            cat_df = cat_df.sort_values("Amount")

            fig_hbar = go.Figure(go.Bar(
                y=cat_df["Category"],
                x=cat_df["Amount"],
                orientation="h",
                marker=dict(color=[cat_color(c) for c in cat_df["Category"]],
                            line=dict(width=0), opacity=0.9),
                text=[f"₹{int(v):,}" for v in cat_df["Amount"]],
                textposition="outside",
                textfont=dict(size=11, family="Inter", color="#8b90a7"),
                hovertemplate="<b>%{y}</b><br>₹%{x:,}<extra></extra>",
            ))
            fig_hbar.update_layout(
                **DARK_LAYOUT,
                title=dict(text="Category Breakdown",
                           font=dict(size=13, color="#fafafa"), x=0, xanchor="left"),
                margin=dict(t=40, b=10, l=10, r=90),
                xaxis=dict(showgrid=True, gridcolor=GRID_COLOR,
                           zeroline=False, showline=False,
                           tickfont=dict(size=10, color=TICK_COLOR)),
                yaxis=dict(showgrid=False, showline=False,
                           tickfont=dict(size=12, color="#fafafa")),
                height=320,
                bargap=0.35,
            )
            st.markdown('<div class="card" style="padding:14px 18px;">', unsafe_allow_html=True)
            st.plotly_chart(fig_hbar, use_container_width=True,
                            config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Monthly bar ───────────────────────────────────────────────────────
        avg_m     = monthly["Amount"].mean()
        max_month = monthly.loc[monthly["Amount"].idxmax(), "Month"]
        m_colors  = ["#4c8bf5" if m == max_month else "#2d3f6e"
                     for m in monthly["Month"]]

        fig_mon = go.Figure()
        fig_mon.add_trace(go.Bar(
            x=monthly["Month"], y=monthly["Amount"],
            marker=dict(color=m_colors, line=dict(width=0)),
            text=[f"₹{int(v):,}" for v in monthly["Amount"]],
            textposition="outside",
            textfont=dict(size=11, family="Inter", color="#8b90a7"),
            hovertemplate="<b>%{x}</b><br>₹%{y:,}<extra></extra>",
        ))
        fig_mon.add_hline(
            y=avg_m, line_dash="dot", line_color="#ea4335", line_width=1.5,
            annotation_text=f"Avg  ₹{int(avg_m):,}",
            annotation_position="top right",
            annotation_font=dict(size=11, color="#ea4335", family="Inter"),
        )
        fig_mon.update_layout(
            **DARK_LAYOUT,
            title=dict(text="📅 Monthly Expenses",
                       font=dict(size=13, color="#fafafa"), x=0, xanchor="left"),
            margin=dict(t=40, b=10, l=10, r=20),
            xaxis=dict(showgrid=False, showline=False, zeroline=False,
                       tickfont=dict(size=12, color=TICK_COLOR)),
            yaxis=dict(showgrid=True, gridcolor=GRID_COLOR,
                       zeroline=False, showline=False,
                       tickprefix="₹", tickfont=dict(size=11, color=TICK_COLOR)),
            height=340, bargap=0.45,
        )
        st.markdown('<div class="card" style="padding:14px 18px;">', unsafe_allow_html=True)
        st.plotly_chart(fig_mon, use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

        # ════════════════════════════════════════════════════════════════════
        #  RECURRING EXPENSE DETECTION
        # ════════════════════════════════════════════════════════════════════
        st.markdown('<p class="sec-label">🔄 Recurring Expenses & Subscriptions</p>', unsafe_allow_html=True)
        
        recurring_df = detect_recurring(df)
        
        if not recurring_df.empty:
            # Summary metrics
            rec_col1, rec_col2, rec_col3 = st.columns(3)
            
            total_recurring_monthly = recurring_df['Amount'].sum()
            total_recurring_annual = recurring_df['Annual'].sum()
            subscription_count = recurring_df['IsSubscription'].sum()
            
            with rec_col1:
                st.markdown(f"""<div class="card">
                    <p class="card-title">Monthly Recurring</p>
                    <p class="card-value">₹{int(total_recurring_monthly):,}</p>
                    <p class="card-sub">from {len(recurring_df)} recurring</p>
                </div>""", unsafe_allow_html=True)
            
            with rec_col2:
                st.markdown(f"""<div class="card">
                    <p class="card-title">Annual Impact</p>
                    <p class="card-value" style="color:#ffb81c;">₹{int(total_recurring_annual):,}</p>
                    <p class="card-sub">committed yearly</p>
                </div>""", unsafe_allow_html=True)
            
            with rec_col3:
                st.markdown(f"""<div class="card">
                    <p class="card-title">Subscriptions</p>
                    <p class="card-value">{subscription_count}</p>
                    <p class="card-sub">identified subscriptions</p>
                </div>""", unsafe_allow_html=True)
            
            # Recurring expenses table
            st.markdown('<p class="sec-label">📋 Recurring Details</p>', unsafe_allow_html=True)
            
            recurring_display = recurring_df[['Description', 'Amount', 'Frequency', 'Annual', 'Count']].copy()
            recurring_display['Amount'] = recurring_display['Amount'].apply(lambda x: f"₹{int(x):,}")
            recurring_display['Annual'] = recurring_display['Annual'].apply(lambda x: f"₹{int(x):,}")
            recurring_display = recurring_display.rename(columns={
                'Description': 'Expense',
                'Amount': 'Per Transaction',
                'Frequency': 'Pattern',
                'Count': 'Occurrences'
            })
            
            # Display as HTML table for better styling
            rec_html = '<table class="tx-table"><thead><tr>'
            for col in recurring_display.columns:
                rec_html += f'<th>{col}</th>'
            rec_html += '</tr></thead><tbody>'
            
            for _, row in recurring_display.iterrows():
                rec_html += '<tr>'
                for col in recurring_display.columns:
                    val = row[col]
                    if col == 'Expense':
                        rec_html += f'<td style="font-weight:500;">{val}</td>'
                    else:
                        rec_html += f'<td>{val}</td>'
                rec_html += '</tr>'
            
            rec_html += '</tbody></table>'
            
            st.markdown('<div class="card" style="padding:14px 18px;">', unsafe_allow_html=True)
            st.markdown(rec_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Optimization suggestions
            st.markdown('<p class="sec-label">💡 Savings Opportunities</p>', unsafe_allow_html=True)
            
            suggestions_html = ""
            
            # Suggestion 1: Consolidate subscriptions
            subscriptions = recurring_df[recurring_df['IsSubscription'] == True]
            if len(subscriptions) > 0:
                sub_total = subscriptions['Annual'].sum()
                suggestions_html += f"""
                <div style="background:#1db679;color:#fff;padding:12px;border-radius:8px;margin-bottom:8px;">
                    <strong>✓ Identified {len(subscriptions)} Subscriptions</strong><br>
                    <span style="font-size:0.9rem;">Annual subscription cost: ₹{int(sub_total):,}</span>
                </div>"""
            
            # Suggestion 2: Find cancelable subscriptions (low frequency)
            low_freq = recurring_df[(recurring_df['IsSubscription'] == True) & (recurring_df['Count'] == 2)]
            if len(low_freq) > 0:
                cancel_savings = low_freq['Annual'].sum()
                suggestions_html += f"""
                <div style="background:#ffb81c;color:#000;padding:12px;border-radius:8px;margin-bottom:8px;">
                    <strong>⚡ Review {len(low_freq)} Low-Frequency Subscriptions</strong><br>
                    <span style="font-size:0.9rem;">Potential savings if cancelled: ₹{int(cancel_savings):,}/year</span>
                </div>"""
            
            # Suggestion 3: Negotiate bills
            bills = recurring_df[recurring_df['Description'].str.lower().str.contains('bill|electricity|water|gas', na=False)]
            if len(bills) > 0:
                bill_total = bills['Annual'].sum()
                suggestions_html += f"""
                <div style="background:#4c8bf5;color:#fff;padding:12px;border-radius:8px;margin-bottom:8px;">
                    <strong>📞 Negotiate {len(bills)} Utility Bills</strong><br>
                    <span style="font-size:0.9rem;">Total annual bills: ₹{int(bill_total):,}</span>
                </div>"""
            
            if not suggestions_html:
                suggestions_html = '<div style="background:#1db679;color:#fff;padding:12px;border-radius:8px;"><strong>✓ No optimization opportunities detected</strong></div>'
            
            st.markdown(suggestions_html, unsafe_allow_html=True)
        
        else:
            st.info("📌 Not enough data to detect recurring expenses. (Need 2+ transactions for same merchant)")

        # ── Weekly trend ──────────────────────────────────────────────────────
        if n >= 5:
            df["Week"] = df["Date"].dt.to_period("W").apply(lambda r: r.start_time)
            wk = df.groupby("Week")["Amount"].sum().abs().reset_index()
            wk.columns = ["Week", "Amount"]

            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=wk["Week"], y=wk["Amount"],
                mode="lines+markers",
                line=dict(color="#4c8bf5", width=2.5),
                marker=dict(size=7, color="#4c8bf5",
                            line=dict(color="#0e1117", width=2)),
                fill="tozeroy", fillcolor="rgba(76,139,245,0.12)",
                hovertemplate="<b>%{x|%b %d}</b><br>₹%{y:,}<extra></extra>",
            ))
            fig_line.update_layout(
                **DARK_LAYOUT,
                title=dict(text="📉 Weekly Spending Trend",
                           font=dict(size=13, color="#fafafa"), x=0, xanchor="left"),
                margin=dict(t=40, b=10, l=10, r=20),
                xaxis=dict(showgrid=False, showline=False, zeroline=False,
                           tickfont=dict(size=11, color=TICK_COLOR)),
                yaxis=dict(showgrid=True, gridcolor=GRID_COLOR,
                           zeroline=False, showline=False,
                           tickprefix="₹", tickfont=dict(size=11, color=TICK_COLOR)),
                height=280,
            )
            st.markdown('<div class="card" style="padding:14px 18px;">', unsafe_allow_html=True)
            st.plotly_chart(fig_line, use_container_width=True,
                            config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")

else:
    st.markdown("""
    <div style="text-align:center;padding:70px 20px;">
        <div style="font-size:3.5rem;margin-bottom:14px;">📊</div>
        <p style="font-size:1.1rem;font-weight:600;color:#fafafa;margin:0 0 8px;">No data yet</p>
        <p style="font-size:0.88rem;color:#8b90a7;margin:0;">
            Upload a CSV with <strong style="color:#fafafa;">Date</strong>,
            <strong style="color:#fafafa;">Description</strong>, and
            <strong style="color:#fafafa;">Amount</strong> columns to get started.
        </p>
    </div>
    """, unsafe_allow_html=True)