import os
import re
import pandas as pd
import streamlit as st

from src.data_ingestion.data_cleaning import DataIngestion
from src.data_ingestion.data_preprocessing import PlotChart

# Create artifacts folder
os.makedirs("artifacts", exist_ok=True)

# Streamlit page config
st.set_page_config(page_title="Data Processing and Visualization App", layout="wide")

st.title("Data Processing and Visualization App")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

def safe_filename(text: str) -> str:
    """
    Convert text into a safe filename part.
    """
    text = str(text).strip().replace(" ", "_")
    text = re.sub(r"[^A-Za-z0-9_\-]+", "", text)
    return text

if uploaded_file is not None:
    try:
        # Save uploaded file
        raw_data_path = os.path.join("artifacts", "Raw_data.xlsx")
        with open(raw_data_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success("File uploaded and saved successfully.")

        # Read preview
        df = pd.read_excel(raw_data_path, header=1)
        df.columns = df.columns.str.strip()

        required_columns = ["OpenTime", "Cluster", "SourceInput", "ClearedDateTime", "EventName"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.error(f"Uploaded file is missing required columns: {missing_columns}")
        else:
            # Normalize display columns
            for col in ["Cluster", "SourceInput", "EventName"]:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip()

            st.subheader("Uploaded File Preview")
            st.dataframe(df.head(), use_container_width=True)

            # Dynamic options from uploaded file
            cluster_options = sorted(df["Cluster"].dropna().unique().tolist())
            operator_options = sorted(df["SourceInput"].dropna().unique().tolist())
            alarm_options = sorted(df["EventName"].dropna().unique().tolist())

            st.subheader("Filter Options")

            col1, col2, col3 = st.columns(3)

            with col1:
                selected_operator = st.multiselect(
                    "Select Operator",
                    options=operator_options,
                    default=[]
                )

            with col2:
                selected_alarm = st.multiselect(
                    "Select Alarm",
                    options=alarm_options,
                    default=[]
                )

            with col3:
                selected_cluster = st.multiselect(
                    "Select Cluster",
                    options=cluster_options,
                    default=[]
                )

            filter_today = st.checkbox("Filter only today's alarms", value=False)

            if st.button("Process and Generate Image"):
                with st.spinner("Processing data..."):
                    try:
                        obj = DataIngestion()

                        clean_data_path = obj.initiate_data_ingestion(
                            operator=selected_operator if selected_operator else None,
                            alarm=selected_alarm if selected_alarm else None,
                            cluster=selected_cluster if selected_cluster else None,
                            filter_today=filter_today
                        )

                        if clean_data_path is None:
                            st.warning("No data found after applying filters.")
                        elif os.path.exists(clean_data_path):
                            st.success(f"Cleaned data saved at: {clean_data_path}")

                            # Load cleaned file
                            df_clean = pd.read_excel(clean_data_path)

                            st.subheader("Cleaned Data")
                            st.dataframe(df_clean, use_container_width=True)

                            if df_clean.empty:
                                st.warning("Cleaned data is empty. Cannot generate image.")
                            else:
                                # Generate image
                                plot_chart = PlotChart(df_clean)
                                image_buffer = plot_chart.create_table_image(show_image=False)

                                st.subheader("Generated Table Image")
                                st.image(image_buffer, caption="Processed Data Table")

                                # Download names
                                operator_str = "_".join(selected_operator) if selected_operator else "AllOperators"
                                alarm_str = "_".join(selected_alarm) if selected_alarm else "AllAlarms"
                                cluster_str = "_".join(selected_cluster) if selected_cluster else "AllClusters"

                                operator_str = safe_filename(operator_str)
                                alarm_str = safe_filename(alarm_str)
                                cluster_str = safe_filename(cluster_str)

                                st.download_button(
                                    label="Download Image",
                                    data=image_buffer,
                                    file_name=f"Processed_Data_{operator_str}_{alarm_str}_{cluster_str}.png",
                                    mime="image/png"
                                )

                                # Optional cleaned Excel download
                                with open(clean_data_path, "rb") as f:
                                    st.download_button(
                                        label="Download Cleaned Excel",
                                        data=f,
                                        file_name="clean_data.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    )
                        else:
                            st.error("Failed to generate cleaned data. File not found.")

                    except Exception as e:
                        st.error(f"An error occurred during processing: {e}")

    except Exception as e:
        st.error(f"Error while reading uploaded file: {e}")