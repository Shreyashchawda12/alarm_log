import pandas as pd
import io
import matplotlib.pyplot as plt
import sys
from dataclasses import dataclass
from src.exception import CustomException
from src.logger import logging

@dataclass
class PlotChartConfig:
    image_filename: str = "Alarm.png"

class PlotChart:
    def __init__(self, df: pd.DataFrame, config: PlotChartConfig = PlotChartConfig()):
        self.df = df
        self.config = config
        logging.info(f"Image will be saved as {self.config.image_filename}")

    def create_table_image(self, width_factors=None, show_image=False, dpi=600):
        try:
            logging.info(f"DataFrame shape before creating image: {self.df.shape}")
            logging.info(f"DataFrame content:\n{self.df.head()}")

            if self.df.empty:
                raise CustomException("DataFrame is empty. Cannot create table image.", sys)

            # Create a figure and axis for the plot
            fig, ax = plt.subplots(figsize=(25, 15))
            ax.xaxis.set_visible(False)
            ax.yaxis.set_visible(False)
            ax.set_frame_on(False)

            # Render the DataFrame as a table
            tbl = ax.table(cellText=self.df.values, colLabels=self.df.columns, cellLoc='center', loc='center')

            # Style the header row
            tbl.auto_set_font_size(False)
            tbl.set_fontsize(10)
            tbl.scale(1, 2)

            for key, cell in tbl.get_celld().items():
                if key[0] == 0:  # Header row
                    cell.set_text_props(weight='bold', color='black')
                    cell.set_facecolor('yellow')

            # Dynamically adjust column width
            if width_factors is None:
                width_factors = {col: 1.5 for col in self.df.columns}

            for col in self.df.columns:
                col_idx = self.df.columns.get_loc(col)
                max_width = max([len(str(item)) for item in self.df[col]]) * width_factors.get(col, 1.5) * 0.004
                for key, cell in tbl.get_celld().items():
                    if key[1] == col_idx:
                        cell.set_width(max_width)

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=dpi)
            buf.seek(0)

            logging.info("Image created in memory.")
            plt.close(fig)

            return buf

        except Exception as e:
            logging.error(f"An error occurred while creating the table image: {str(e)}", exc_info=True)
            raise CustomException(e, sys)  # Ensure sys is passed to capture traceback context
