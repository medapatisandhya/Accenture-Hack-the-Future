import pandas as pd
import ast
import streamlit as st
import matplotlib.pyplot as plt

# Load and preprocess data
def load_and_process_data():
    customer_df = pd.read_csv("data/customer_data_collection.csv")
    product_df = pd.read_csv("data/product_recommendation_data.csv")

    customer_df['Browsing_History'] = customer_df['Browsing_History'].apply(ast.literal_eval)
    customer_df['Purchase_History'] = customer_df['Purchase_History'].apply(ast.literal_eval)

    customer_df['Preferred_Category'] = customer_df['Browsing_History'].apply(
        lambda x: max(set(x), key=x.count) if x else None)

    customer_df = customer_df.loc[:, ~customer_df.columns.str.contains('^Unnamed')]
    product_df = product_df.loc[:, ~product_df.columns.str.contains('^Unnamed')]

    def recommend_product(preferred_category):
        match = product_df[product_df['Category'].str.lower() == str(preferred_category).lower()]
        if not match.empty:
            return match.sample(1).iloc[0]
        else:
            return product_df.sample(1).iloc[0]

    recommended_products = [recommend_product(cat).to_dict() for cat in customer_df['Preferred_Category']]
    recommendations_df = pd.DataFrame(recommended_products)

    # Rename duplicate columns in product dataset
    recommendations_df = recommendations_df.rename(columns={
        'Holiday': 'Product_Holiday',
        'Season': 'Product_Season',
        'Geographical_Location': 'Product_Location'
    })

    customer_360_df = pd.concat([customer_df.reset_index(drop=True), recommendations_df.reset_index(drop=True)], axis=1)
    return customer_360_df

df = load_and_process_data()

st.set_page_config(page_title="Customer 360 Dashboard", layout="wide")
st.title("📊 Customer 360 Recommendation Dashboard")

st.subheader("🔍 Key Insights")
col1, col2, col3 = st.columns(3)
col1.metric("Total Customers", len(df))
col2.metric("Unique Categories", df['Preferred_Category'].nunique())
product_col = 'Product_ID' if 'Product_ID' in df.columns else df.columns[-1]
col3.metric("Products Used", df[product_col].nunique())

# Preferred Categories
st.subheader("📈 Preferred Categories by Customers")
category_counts = df['Preferred_Category'].value_counts()
fig1, ax1 = plt.subplots()
ax1.bar(category_counts.index, category_counts.values, color="skyblue")
plt.xticks(rotation=45)
st.pyplot(fig1)

# Customer Segment Analysis
if 'Customer_Segment' in df.columns:
    st.subheader("📊 Customer Segment Distribution")
    segment_counts = df['Customer_Segment'].value_counts()
    fig_seg, ax_seg = plt.subplots()
    ax_seg.bar(segment_counts.index, segment_counts.values, color="lightgreen")
    st.pyplot(fig_seg)

# Gender Pie Chart
if 'Gender' in df.columns:
    st.subheader("🧬 Gender Distribution")
    gender_counts = df['Gender'].value_counts()
    fig_gender, ax_gender = plt.subplots()
    ax_gender.pie(gender_counts.values, labels=gender_counts.index, autopct='%1.1f%%', startangle=90)
    ax_gender.axis('equal')
    st.pyplot(fig_gender)

# Location Pie Chart
if 'Location' in df.columns:
    st.subheader("🌍 Customer Locations Distribution")
    location_counts = df['Location'].value_counts()
    fig2, ax2 = plt.subplots()
    ax2.pie(location_counts.values, labels=location_counts.index, autopct='%1.1f%%')
    st.pyplot(fig2)

# Filter Recommendations
st.subheader("🔎 Filter Recommendations by Category")
selected_cat = st.selectbox("Choose a category", df['Preferred_Category'].unique())
filtered = df[df['Preferred_Category'] == selected_cat]
st.dataframe(filtered)

# Full Table
st.subheader("📋 Full Customer 360 Data")
with st.expander("Show complete data table"):
    st.dataframe(df)

# Download as CSV
st.download_button("📥 Download Customer 360 as CSV", data=df.to_csv(index=False), file_name="customer360.csv", mime='text/csv')
