import os
import sys
import pandas as pd
from datetime import datetime
from dataclasses import dataclass
from src.exception import CustomException
from src.logger import logging


@dataclass
class DataIngestionConfig:
    raw_data_path: str = os.path.join("artifacts", "Raw_data.xlsx")
    clean_data_path: str = os.path.join("artifacts", "clean_data.xlsx")


class DataIngestion:
    DROP_COLUMNS = [
        "Status",
        "Severity",
        "TTNumber",
        "CustomerSiteId",
        "CreatedUser",
        "TTAgeing",
        "Technician",
        "Supervisor",
        "COMH",
        "EscaltionstatusLastupdateddt",
        "SystemRCAService",
        "EsclationStatus",
        "ClearedDateTime",
        "Circle",
        "SiteClasification",
        "VNOCTTProcessTime"
    ]

    REQUIRED_COLUMNS = [
        "OpenTime",
        "Cluster",
        "SourceInput",
        "ClearedDateTime",
        "EventName",
        "ClusterIncharge",
        "ClusterEngineer"
    ]

    def __init__(self):
        self.ingestion_config = DataIngestionConfig()

    @staticmethod
    def normalize_text_series(series: pd.Series) -> pd.Series:
        """
        Normalize text values for reliable filtering.
        """
        return (
            series.astype(str)
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

    @staticmethod
    def normalize_filter_values(values):
        """
        Normalize filter list values.
        """
        if values is None:
            return None
        return [str(value).strip() for value in values if pd.notna(value)]

    def initiate_data_ingestion(
        self,
        operator: list = None,
        alarm: list = None,
        cluster: list = None,
        target_date=None,
        filter_today: bool = True
    ):
        logging.info("Data Ingestion method starts")

        try:
            raw_path = self.ingestion_config.raw_data_path

            if not os.path.exists(raw_path):
                raise FileNotFoundError(f"Raw data file not found at {raw_path}")

            # Read Excel file
            df = pd.read_excel(raw_path, header=1)
            logging.info(f"Dataset read as pandas DataFrame with shape {df.shape}")

            # Clean column names
            df.columns = df.columns.str.strip()

            # Check required columns
            missing_columns = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns in input file: {missing_columns}")

            # Normalize important text columns
            text_columns = ["Cluster", "SourceInput", "EventName", "ClusterIncharge", "ClusterEngineer"]
            for col in text_columns:
                if col in df.columns:
                    df[col] = self.normalize_text_series(df[col])

            # Convert datetime columns safely
            df["OpenTime"] = pd.to_datetime(df["OpenTime"], dayfirst=True, errors="coerce")
            df["ClearedDateTime"] = pd.to_datetime(df["ClearedDateTime"], dayfirst=True, errors="coerce")

            # Drop rows where OpenTime is invalid
            df = df.dropna(subset=["OpenTime"])
            logging.info(f"Rows after valid OpenTime conversion: {df.shape[0]}")

            # Filter by date if required
            if target_date is not None:
                target_date = pd.to_datetime(target_date).date()
                df = df[df["OpenTime"].dt.date == target_date]
                logging.info(f"Filtered by target_date={target_date}, remaining rows: {df.shape[0]}")
            elif filter_today:
                today_date = datetime.today().date()
                df = df[df["OpenTime"].dt.date == today_date]
                logging.info(f"Filtered by today's date={today_date}, remaining rows: {df.shape[0]}")
            else:
                logging.info("Date filtering skipped")

            if df.empty:
                logging.warning("No data found after date filtering")
                return None

            # Keep only uncleared alarms
            df = df[df["ClearedDateTime"].isna()]
            logging.info(f"Filtered by uncleared alarms, remaining rows: {df.shape[0]}")

            if df.empty:
                logging.warning("No uncleared alarms found")
                return None

            # Normalize filter inputs
            cluster = self.normalize_filter_values(cluster)
            operator = self.normalize_filter_values(operator)
            alarm = self.normalize_filter_values(alarm)

            # Apply cluster filter only if provided
            if cluster:
                df = df[df["Cluster"].isin(cluster)]
                logging.info(f"Filtered by cluster list, remaining rows: {df.shape[0]}")
                if df.empty:
                    logging.warning("No data found after cluster filtering")
                    return None
            else:
                logging.info("No cluster filter provided, using all clusters from file")

            # Apply operator filter only if provided
            if operator:
                df = df[df["SourceInput"].isin(operator)]
                logging.info(f"Filtered by operator list, remaining rows: {df.shape[0]}")
                if df.empty:
                    logging.warning("No data found after operator filtering")
                    return None
            else:
                logging.info("No operator filter provided, using all operators from file")

            # Apply alarm filter only if provided
            if alarm:
                df = df[df["EventName"].isin(alarm)]
                logging.info(f"Filtered by alarm list, remaining rows: {df.shape[0]}")
                if df.empty:
                    logging.warning("No data found after alarm filtering")
                    return None
            else:
                logging.info("No alarm filter provided, using all alarms from file")

            # Sort data
            sort_columns = [col for col in ["ClusterIncharge", "ClusterEngineer"] if col in df.columns]
            if sort_columns:
                df = df.sort_values(by=sort_columns, na_position="last")
                logging.info(f"Data sorted by {sort_columns}")

            # Drop unnecessary columns
            df = df.drop(columns=self.DROP_COLUMNS, errors="ignore")
            logging.info(f"Columns dropped, final DataFrame shape: {df.shape}")

            # Create artifacts folder and save cleaned file
            os.makedirs(os.path.dirname(self.ingestion_config.clean_data_path), exist_ok=True)
            df.to_excel(self.ingestion_config.clean_data_path, index=False)
            logging.info(f"Clean data saved at {self.ingestion_config.clean_data_path}")

            return self.ingestion_config.clean_data_path

        except Exception as e:
            logging.error("Exception occurred during data ingestion", exc_info=True)
            raise CustomException(e, sys)