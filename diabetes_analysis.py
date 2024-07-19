import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Define the file path
file_path = os.path.join(os.path.dirname(__file__), 'Ravikanth_Narayanabhatla_ZivovGlucoseData.xlsx')

# Load the data
try:
    glucose_data = pd.read_excel(file_path)
    glucose_data['Time'] = pd.to_datetime(glucose_data['Time'], format='%b %d %Y, %I:%M %p')
except Exception as e:
    st.error(f"Error loading data: {e}")
    glucose_data = pd.DataFrame()  # Create an empty DataFrame in case of error

# Streamlit app layout
st.title("Diabetes Glucose Analysis")

st.sidebar.header("Filters")

# X-axis selection
x_axis = st.sidebar.selectbox("Select X-axis", ['Time', 'Glucose Value'], index=0)

# Y-axis selection
y_axis = st.sidebar.selectbox("Select Y-axis", ['Time', 'Glucose Value'], index=1)

# Glucose value range filter
glucose_min, glucose_max = st.sidebar.slider(
    "Filter Glucose Values",
    min_value=float(glucose_data['Glucose Value'].min()),
    max_value=float(glucose_data['Glucose Value'].max()),
    value=(float(glucose_data['Glucose Value'].min()), float(glucose_data['Glucose Value'].max()))
)

# Time range filter
start_date, end_date = st.sidebar.date_input(
    "Filter Time Range",
    value=[glucose_data['Time'].min(), glucose_data['Time'].max()],
    min_value=glucose_data['Time'].min(),
    max_value=glucose_data['Time'].max()
)

# Filter data based on user input
filtered_data = glucose_data[
    (glucose_data['Glucose Value'] >= glucose_min) &
    (glucose_data['Glucose Value'] <= glucose_max) &
    (glucose_data['Time'] >= pd.to_datetime(start_date)) &
    (glucose_data['Time'] <= pd.to_datetime(end_date))
]

# Display summary statistics
st.header("Summary Statistics")
st.write(f"Minimum Glucose Level: {filtered_data['Glucose Value'].min()} mg/dL")
st.write(f"Maximum Glucose Level: {filtered_data['Glucose Value'].max()} mg/dL")
st.write(f"Average Glucose Level: {filtered_data['Glucose Value'].mean():.2f} mg/dL")
st.write(f"Hypoglycemia Count: {(filtered_data['Glucose Value'] < 70).sum()}")
st.write(f"Hyperglycemia Count: {(filtered_data['Glucose Value'] > 180).sum()}")

# Create and configure the Plotly graph
fig = px.line(filtered_data, x=x_axis, y=y_axis, title='Glucose Levels')

# Update layout for responsiveness
fig.update_layout(
    autosize=True,  # Allow the chart to resize automatically
    margin=dict(l=40, r=40, t=40, b=40),  # Add margins to avoid clipping
    title=dict(x=0.5),  # Center the title
    xaxis_title=x_axis,
    yaxis_title=y_axis
)

# Display the Plotly graph in Streamlit
st.plotly_chart(fig, use_container_width=True)
