import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh
import matplotlib.pyplot as plt
import seaborn as sns

st.markdown("---")

st.set_page_config(page_title="European Bank Churn Dashboard",layout="wide")

st.title("European Bank Churn Dashboard")

#Load Dataset
df= pd.read_csv("European_Bank.csv")

st.sidebar.header("Dashboard Filters")

selected_geo=st.sidebar.multiselect("Select Geography",options=df["Geography"].unique(),default=df["Geography"].unique(),key="geo_filter")

selected_churn=st.sidebar.multiselect("Select Churn Status",options=[0,1],default=[0,1],key="churn_filter")

high_value_only=st.sidebar.checkbox("High Value Customers Only",key="high_value_1")

filtered_df=df[(df["Geography"].isin(selected_geo)) & (df["Exited"].isin(selected_churn))]

if high_value_only:
   balance_threshold=filtered_df["Balance"].median()

   filtered_df=filtered_df[(filtered_df["Balance"]>balance_threshold) | (filtered_df["NumOfProducts"]>=3)]


# =============================
# Overall Churn Rate
# ===============================
overall_churn_rate=filtered_df["Exited"].mean()*100
total_customers=len(filtered_df)
total_churned=filtered_df["Exited"].sum()

# ===============================
# Segment Churn Rate
# ===============================
segment_churn_rate=filtered_df.groupby("Gender")["Exited"].mean()*100

highest_segment=segment_churn_rate.idxmax()
highest_segment_rate=segment_churn_rate.max()

# ===============================
# High Value Churn
# ===============================
balance_threshold=df["Balance"].median()

high_value_df=filtered_df[(filtered_df["Balance"]>balance_threshold) | (filtered_df["NumOfProducts"]>=3)]

high_value_churn_ratio=high_value_df["Exited"].mean()*100
# ============================
# Engagement Risk Indicator
# ============================
inactive_df=filtered_df[filtered_df["IsActiveMember"]==0]

engagement_drop=inactive_df["Exited"].mean()*100
# ============================
# Geo Risk Index
# ============================

geo_df=filtered_df[filtered_df["Geography"].isin(selected_geo)]

geo_risk=geo_df["Exited"].mean()*100

col1,col2,col3,col4,col5=st.columns(5)

with col1:
          st.metric("Overall Churn Rate",f"{overall_churn_rate:.2f}%",f"{total_churned} churned")

with col2:
          st.metric("Highest Segment Churn",f"{highest_segment_rate:.2f}%",highest_segment)

with col3:
          st.metric("High Value Churn Rate",f"{high_value_churn_ratio:.2f}%",f"{len(high_value_df)} customers")

with col4:
          st.metric("Engagement Risk",f"{engagement_drop:.2f}%",f"{len(inactive_df)} inactive")    

with col5:
          st.metric("Geographic Risk",f"{geo_risk:.2f}%",highest_segment)

# ===============================
# SIDEBAR FILTERS
# ===============================

st.sidebar.header("Filter Options")

selected_country = st.sidebar.multiselect("Select Geography",options=filtered_df["Geography"].unique(),default=filtered_df["Geography"].unique())

selected_gender = st.sidebar.multiselect("Select Gender",options=filtered_df["Gender"].unique(),default=filtered_df["Gender"].unique())

filtered_df =filtered_df[(filtered_df["Geography"].isin(selected_country)) & (filtered_df["Gender"].isin(selected_gender))]

st.subheader("Dataset Preview")

st.dataframe(df.head())

# ================================
# METRICS
# ================================

segment_filter=st.selectbox("Select Segment",["All","High Value","Medium Value","Low Value","Male","Female","Age"])

if segment_filter=="All":
   filtered_df=df
else:
     filtered_df=filtered_df[filtered_df["Gender"]==segment_filter]

col1,col2,col3=st.columns(3)

with col1:
     st.subheader("Overall Churn Rate")
     fig1,ax1=plt.subplots(figsize=(5,6))
     sns.countplot(data=filtered_df,x="Exited",palette=["#2CA02C","#D62728"],ax=ax1)
     st.pyplot(fig1,use_container_width=False)

with col2:
          st.subheader("Segment Churn Rate (Gender)")
          fig2,ax2=plt.subplots(figsize=(5,6))
        
          sns.countplot(data=filtered_df,x="Gender",hue="Exited",palette=["#3498db","#e74c3c"],ax=ax2)
         
          st.pyplot(fig2,use_container_width=False)
     
with col3:
     st.subheader("Geographic Risk Index)")
     geo_risk=(filtered_df.groupby("Geography")["Exited"].mean().reset_index(name="ChurnRate"))

     fig3,ax3=plt.subplots(figsize=(5,6))
     sns.barplot(data=geo_risk,x="Geography",y="ChurnRate",palette=["#1F77B4","#FF7F0E","#2CA02C"],ax=ax3)
     ax3.set_xlabel("Geography")
     ax3.set_ylabel("Churn Rate")
     ax3.set_title("Geographic Risk Index")

     st.pyplot(fig3,use_container_width=False)

col1,col2=st.columns(2)

with col1:
     st.subheader("Engagement Drop vs Churn")

     filtered_df["Engagement_Level"]=filtered_df["NumOfProducts"].apply(lambda x:"Low Engagement" if x==1 else "High Engagement")

     fig1,ax1=plt.subplots()
     sns.countplot(x="Engagement_Level",hue="Exited",data=filtered_df,ax=ax1)
     ax1.set_title("Engagement Level vs Churn")
     ax1.set_xlabel("Engagement Level")
     ax1.set_ylabel("Customer Count")

     st.pyplot(fig1,use_container_width=False)

with col2:
     st.subheader("High Value Customer Churn")
     filtered_df["High_Value"]=filtered_df["Balance"].apply(lambda x:"High Value" if x>100000 else "Normal Values")
     
     fig2,ax2=plt.subplots()
     sns.countplot(x="High_Value",hue="Exited",data=filtered_df,ax=ax2)
     ax2.set_title("High Value Customers vs Churn")
     ax2.set_xlabel("Customer Segment")
     ax2.set_ylabel("Customer Count")
    
     st.pyplot(fig2,use_container_width=False)

# ================================
# CHURN DISTRIBUTION
# ================================

st.subheader("Churn Distribution")

col1,col2=st.columns(2)

with col1:
     fig1,ax1=plt.subplots(figsize=(4,3))
     sns.countplot(x="Exited",data=filtered_df,ax=ax1,palette=["#4CAF50","#F44336"])
     ax1.set_title("Customer Churn Count")
     ax1.set_xlabel("Churn (0=Retained,1=Churned)")
     ax1.set_ylabel("Count")
     st.pyplot(fig1,use_container_width=False)

with col2:
     churn_percent=filtered_df["Exited"].value_counts(normalize=True)*100

     fig2,ax2=plt.subplots(figsize=(4,3))

     ax2.bar(churn_percent.index.astype(str),churn_percent.values,color=["#4CAF50","#F44336"])
     ax2.set_title("CustomerChurn Percentage")
     ax2.set_xlabel("Churn (0=Retained,1=Churned)")
     ax2.set_ylabel("Percentage (%)")
     st.pyplot(fig2,use_container_width=False)

# ================================
# AGE DISTRIBUTION VS BALANCE DISTRIBUTION
# ================================
st.subheader("AGE DISTRIBUTION VS BALANCE DISTRIBUTION")

col1,col2=st.columns([1,1])

with col1:
     fig,ax=plt.subplots(figsize=(4,3))
     sns.histplot(filtered_df["Age"],kde=True,ax=ax,bins=30,color="#4CAF50")
     ax.set_title("Age Distribution")
     st.pyplot(fig,use_container_width=False)

with col2:
     fig2,ax2=plt.subplots(figsize=(4,3))
     sns.histplot(filtered_df["Balance"],kde=True,ax=ax2,bins=30,color="#F44336")
     ax2.set_title("Balance Distribution")
     st.pyplot(fig2,use_container_width=False)


st.markdown("---")

col1,col2=st.columns(2)

with col1:
     st.header("Overall Churn Summary")
     
     if filtered_df.empty:
        st.warning("No data available for selected filter")
     else:
          values=filtered_df["Exited"].value_counts().sort_index()
          
          fig,ax=plt.subplots(figsize=(4,4))
          ax.pie(values,labels=["Stayed","Churned"],autopct="%1.1f%%",colors=["#4CAF50","#F44336"],startangle=90)
          ax.set_title("Churn Share")
          st.pyplot(fig,use_container_width=False)

with col2:
     st.write("### Insight")
     churn_rate=(filtered_df["Exited"].sum()/len(df))*100
     st.write(f"Overall churn rate is **{churn_rate:.2f}%**.")


st.markdown("---")
st.header("Geography-wise churn visualization")

selected_country=st.sidebar.multiselect("Select Geography",options=df["Geography"].unique())

if selected_country:
   filtered_df=df[df["Geography"].isin(selected_country)]
else:
      filtered_df=df.copy()

geo_churn=(filtered_df.groupby("Geography")["Exited"].mean().mul(100).reset_index(name="ChurnRate"))
geo_churn_columns=["Geography","ChurnRate"]

st.markdown("### Geography-wise Churn Rate")

selected_geo=st.selectbox("Select Geography to Drill Down",filtered_df["Geography"].unique())
col1,col2=st.columns(2)

with col1:
     fig1,ax1=plt.subplots(figsize=(6,6))
     sns.barplot(data=geo_churn,x="Geography",y="ChurnRate",palette=     ["#1F77B4","#2CA02C","#D62728"],ax=ax1)
     ax1.set_title("Churn Rate by Geography")
     ax1.set_ylabel("Churn Rate(%)")
     st.pyplot(fig1,use_container_width=False)

st.markdown("---")
st.header("Age and Tenure Churn Comparison")

col1,col2=st.columns(2)

with col1:
     fig1,ax1=plt.subplots(figsize=(4,3))
     sns.boxplot(x="Exited",y="Age",data=filtered_df,ax=ax1,palette=["#4CAF50","#F44336"])
     ax1.set_title("Age vs Churn")
     ax1.set_xlabel("Churn (0=Retained,1=Churned)")
     ax1.set_ylabel("Age")
     st.pyplot(fig1,use_container_width=False)

with col2:
     fig2,ax2=plt.subplots(figsize=(4,3))
     sns.boxplot(x="Exited",y="Tenure",data=filtered_df,ax=ax2,palette=["#4CAF50","#F44336"])
     ax2.set_title("Tenure vs Churn")
     ax2.set_xlabel("Churn (0=Retained,1=Churned")
     ax2.set_ylabel("Tenure")
     st.pyplot(fig2,use_container_width=False)

st.subheader("Engagement and Tenure Patterns")

col1,col2=st.columns(2)

with col1:
          fig1,ax1=plt.subplots()
          sns.histplot(filtered_df['Tenure'],bins=10,kde=True,color="#4CAF50",ax=ax1)
          ax1.set_title("Tenure Distribution")
          st.pyplot(fig1,use_container_width=False)

with col2:
          fig2,ax2=plt.subplots()
          sns.boxplot(x='IsActiveMember',y='Tenure',data=filtered_df,color="#2196F3",ax=ax2)
          ax2.set_title("Active Member vs Tenure")
          st.pyplot(fig2,use_container_width=False)

col3,col4=st.columns(2)

with col3:
          fig3,ax3=plt.subplots()
          sns.boxplot(x='NumOfProducts',y='Tenure',data=filtered_df,color="#FF9800",ax=ax3)
          ax3.set_title("Products vs Tenure")
          st.pyplot(fig3,use_container_width=False)
with col4:
          fig4,ax4=plt.subplots()
          sns.countplot(x='IsActiveMember',hue='Exited',data=filtered_df,ax=ax4)
          ax4.set_title("Engagement vs Churn")
          st.pyplot(fig4,use_container_width=False)


balance_threshold=df["Balance"].median()

high_value_filtered_df=filtered_df[(filtered_df["Balance"]>balance_threshold) | (filtered_df["NumOfProducts"]>=3)]

st.markdown("## High-Value Customer Churn Explorer")

col1,col2=st.columns(2)

with col1:
     churn_counts=high_value_filtered_df["Exited"].value_counts()

     fig1,ax1=plt.subplots(figsize=(4,4))
     ax1.pie(churn_counts,labels=["Retained","Churned"],autopct="%1.1f%%",colors=["#4CAF50","#F44336"],startangle=90)
     ax1.set_title("High Value Churn Distribution")

     st.pyplot(fig1,use_container_width=False)

with col2:
     avg_balance=(high_value_filtered_df.groupby("Exited")["Balance"].mean().reset_index())
   
     fig2,ax2=plt.subplots(figsize=(4,4))
     ax2.bar(["Retained","Churned"],avg_balance["Balance"],color=["#4CAF50","#F44336"])
     ax2.set_title("Avg Balance: Retained vs Churned")
     ax2.set_ylabel("Average Balance")

     st.pyplot(fig2,use_container_width=False)
     

