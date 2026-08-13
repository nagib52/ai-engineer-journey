import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="AI Inventory & Purchase Assistant", layout="wide")
st.title(" AI Inventory and Purchase Recommendation Assistant")
st.write("Upload your inventory data to get AI-powered restock recommendations and slow-moving item detection.")

# ===== File Upload =====
uploaded_file = st.file_uploader("Upload Inventory CSV/Excel", type=["csv", "xlsx"])

use_sample = st.checkbox("Use sample data instead (inventory.csv)", value=True if not uploaded_file else False)

df = None
if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
elif use_sample and os.path.exists("inventory.csv"):
    df = pd.read_csv("inventory.csv")

# ===== Analysis Functions =====
def calculate_metrics(df):
    df["days_until_stockout"] = df.apply(
        lambda row: round(row["current_stock"] / row["avg_daily_sales"], 1) if row["avg_daily_sales"] > 0 else 999,
        axis=1
    )
    df["is_low_stock"] = df["current_stock"] <= df["reorder_level"]
    df["is_slow_moving"] = df["avg_daily_sales"] < 1.0
    df["suggested_order_qty"] = df.apply(
        lambda row: max(0, round((row["avg_daily_sales"] * (row["lead_time_days"] + 14)) - row["current_stock"]))
        if row["is_low_stock"] else 0,
        axis=1
    )
    return df

def get_ai_recommendation(row):
    prompt = f"""You are an inventory management expert. Analyze this item and give a short, practical recommendation.

Item: {row['item_name']}
Current Stock: {row['current_stock']}
Reorder Level: {row['reorder_level']}
Avg Daily Sales: {row['avg_daily_sales']}
Lead Time (days): {row['lead_time_days']}
Days Until Stockout: {row['days_until_stockout']}
Is Low Stock: {row['is_low_stock']}
Is Slow Moving: {row['is_slow_moving']}
Suggested Order Quantity: {row['suggested_order_qty']}

Give a 2-3 sentence recommendation on what action to take (reorder now, hold off, discount to clear slow stock, etc.) and why.
"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# ===== UI =====
if df is not None:
    st.subheader(" Raw Inventory Data")
    st.dataframe(df, use_container_width=True)

    df = calculate_metrics(df)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Items", len(df))
    col2.metric("Low Stock Items", int(df["is_low_stock"].sum()))
    col3.metric("Slow Moving Items", int(df["is_slow_moving"].sum()))

    if st.button(" Get AI Recommendations"):
        low_priority_df = df[df["is_low_stock"] | df["is_slow_moving"]]

        if low_priority_df.empty:
            st.success("All items are healthy — no urgent action needed!")
        else:
            st.subheader(" AI Recommendations (items needing attention)")
            progress = st.progress(0)
            for i, (_, row) in enumerate(low_priority_df.iterrows()):
                recommendation = get_ai_recommendation(row)

                if row["is_low_stock"]:
                    tag = "🔴 LOW STOCK"
                elif row["is_slow_moving"]:
                    tag = "🟡 SLOW MOVING"
                else:
                    tag = "🟢"

                with st.expander(f"{tag} — {row['item_name']} (Stock: {row['current_stock']}, Stockout in ~{row['days_until_stockout']} days)"):
                    c1, c2 = st.columns(2)
                    c1.write(f"**Reorder Level:** {row['reorder_level']}")
                    c1.write(f"**Avg Daily Sales:** {row['avg_daily_sales']}")
                    c2.write(f"**Lead Time:** {row['lead_time_days']} days")
                    c2.write(f"**Suggested Order Qty:** {row['suggested_order_qty']}")
                    st.write("**AI Recommendation:**")
                    st.info(recommendation)

                progress.progress((i + 1) / len(low_priority_df))
else:
    st.info("Upload a CSV/Excel file, or check 'Use sample data' to try it with demo inventory.")