import os
import pandas as pd
import streamlit as st
from src.data_ingestion.data_cleaning import DataIngestion
from src.data_ingestion.data_preprocessing import PlotChart

# Streamlit App Title
st.title("Data Processing and Visualization App")

# Upload the file
uploaded_file = st.file_uploader("Upload your Excel file", type=['xlsx'])

# Check if a file was uploaded
if uploaded_file is not None:
    # Save the uploaded file to the artifacts folder
    file_path = os.path.join('artifacts', 'Raw_data.xlsx')
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"File uploaded and saved to {file_path}")

    # Load the data to preview in the app
    df = pd.read_excel(file_path)
    st.dataframe(df.head())  # Display first few rows for verification

    # Provide dropdowns for filters (operators, alarms, clusters)
    operator = st.multiselect("Select Operator", ['Airtel Dumps', 'RJIO', 'Vodafone Dumps', 'Mobile'])
    alarm = st.multiselect("Select Alarms", ['Battery Discharge/Low battery', 'Mains Fail/EB Fail',
                                             'SITE ON BATTERY', 'RU LOW VOLTAGE', '4G OUTAGE', '2G OUTAGE'])
    cluster = st.multiselect("Select Cluster", ['Aurangabad', 'Nashik', 'Pune-1', 'Akola', 'Ahmednagar',
                                                'Nagpur', 'Latur', 'Pune-3', 'Kolhapur', 'Pune-2', 'Goa',
                                                'Solapur'])

    # Process the data after button click
    if st.button("Process and Generate Image"):
        # Initiate data ingestion
        obj = DataIngestion()
        clean_data_path = obj.initiate_data_ingestion(operator, alarm, cluster)
        st.success(f"Cleaned data saved at: {clean_data_path}")

        # Load the cleaned data
        if os.path.exists(clean_data_path):
            df_clean = pd.read_excel(clean_data_path)
            st.dataframe(df_clean.head())  # Show the cleaned data for review

            # Generate the image using PlotChart
            plot_chart = PlotChart(df_clean)
            image_path = plot_chart.create_table_image(show_image=False)
            st.success(f"Image saved at: {image_path}")

            # Display the image in the Streamlit app
            st.image(image_path, caption='Processed Data Table')
        else:
            st.error("Failed to generate cleaned data.")
