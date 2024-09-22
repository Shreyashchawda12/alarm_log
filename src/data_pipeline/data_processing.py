import os
import sys
import pandas as pd

# Assuming logging and CustomException are implemented in your project
# from logger import logging
# from exception import CustomException

# Adjust the path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import your classes
from src.exception import CustomException
from src.logger import logging
from src.data_ingestion.data_cleaning import DataIngestion
from src.data_ingestion.data_preprocessing import PlotChart 

if __name__ == '__main__':
    operator = ['Vodafone Dumps']
    alarm = ['4G OUTAGE']
    
    try:
        # Initiate data ingestion
        obj = DataIngestion()
        clean_data_path = obj.initiate_data_ingestion(operator, alarm)
        logging.info
        (f"Cleaned data saved at: {clean_data_path}")
        
        # Check if the clean data exists and load it
        if os.path.exists(clean_data_path):
            df = pd.read_excel(clean_data_path)
            logging.info(f"Data loaded: {df.head()}") 
             
            
            # Check type before passing to PlotChart
            logging.info(f"Type of data passed to PlotChart: {type(df)}") 
            
            # Pass DataFrame to PlotChart
            plot_chart = PlotChart(df)
            image_path = plot_chart.create_table_image()
            logging.info(f"Table image saved at: {image_path}")
        else:
            logging.info(f"Cleaned data not found at {clean_data_path}")
    
    except CustomException as e:
        logging.error(f"CustomException occurred: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
