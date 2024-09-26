import os
import pandas as pd
import streamlit as st
from io import BytesIO
from src.data_ingestion.data_cleaning import DataIngestion
from src.data_ingestion.data_preprocessing import PlotChart

# Create an artifacts folder if it doesn't exist
os.makedirs('artifacts', exist_ok=True)

# Streamlit App Title
st.title("Data Processing and Visualization App")

# Upload the file
uploaded_file = st.file_uploader("Upload your Excel file", type=['xlsx'])

# Check if a file was uploaded
if uploaded_file is not None:
    # Save the uploaded file in the artifacts folder
    raw_data_path = os.path.join('artifacts', 'Raw_data.xlsx')
    
    with open(raw_data_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("File uploaded and saved as raw data.")

    # Load the data to preview in the app
    df = pd.read_excel(raw_data_path, header = 1)
    df.columns = df.columns.str.strip()
    
    # Validate the structure of the DataFrame (e.g., required columns)
    required_columns = ['OpenTime', 'Cluster', 'SourceInput', 'ClearedDateTime', 'EventName']
    if not all(col in df.columns for col in required_columns):
        st.error("Uploaded file is missing required columns.")
    else:
        st.dataframe(df.head())  # Display first few rows for verification

        # Provide dropdowns for filters (operators, alarms, clusters)
        operator = st.multiselect("Select Operator", ['Airtel Dumps', 'RJIO', 'Vodafone Dumps', 'Mobile'])
        alarm = st.multiselect("Select Alarms", ['Battery Discharge/Low battery', 'Mains Fail/EB Fail',
                                                 'SITE ON BATTERY', 'RU LOW VOLTAGE', '4G OUTAGE', '2G OUTAGE'])
        cluster = st.multiselect("Select Cluster", ['Aurangabad', 'Nashik', 'Pune-1', 'Akola', 'Ahmednagar',
                                                    'Nagpur', 'Latur', 'Pune-3', 'Kolhapur', 'Pune-2', 'Goa',
                                                    'Solapur'])

        # Validate that user has selected at least one option in each category
        if st.button("Process and Generate Image"):
            if not operator or not alarm or not cluster:
                st.error("Please select at least one Operator, Alarm, and Cluster to process the data.")
            else:
                with st.spinner("Processing data..."):
                    try:
                        # Initiate data ingestion
                        obj = DataIngestion()
                        clean_data_path = obj.initiate_data_ingestion(operator, alarm, cluster)

                        if clean_data_path and os.path.exists(clean_data_path):
                            st.success(f"Cleaned data saved at: {clean_data_path}")

                            # Load the cleaned data from the file path into a DataFrame
                            df_clean = pd.read_excel(clean_data_path)  # Read the Excel file into a DataFrame
                            st.dataframe(df_clean)  # Show the cleaned data for review

                            # Generate the image using PlotChart
                            plot_chart = PlotChart(df_clean)
                            image_bytes = plot_chart.create_table_image(show_image=False)

                            # Display the image in the Streamlit app
                            st.image(image_bytes, caption='Processed Data Table')

                            # Create a formatted string for the download file name
                            operator_str = "_".join(operator)
                            alarm_str = "_".join(alarm)
                            cluster_str = "_".join(cluster)

                            # Provide a download button for the image
                            st.download_button(
                                label="Download Image",
                                data=image_bytes,
                                file_name=f"Processed_Data_{operator_str}_{alarm_str}_{cluster_str}.png",
                                mime="image/png"
                            )
                        else:
                            st.error("Failed to generate cleaned data. File not found.")
                    
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
