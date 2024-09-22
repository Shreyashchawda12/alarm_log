import os
import io
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from dataclasses import dataclass
from src.exception import CustomException
from src.logger import logging  # Ensure logger is properly set up in your project

@dataclass
class PlotChartConfig:
    image_filename: str = f"Alarm.png"

    @property
    def image_path(self):
        # Remove downloads_dir since cloud environments do not support this
        return self.image_filename  # Use just the image filename

class PlotChart:
    def __init__(self, df: pd.DataFrame, config: PlotChartConfig = PlotChartConfig()):
        """
        Initializes the PlotChart class.

        Parameters:
        df (pd.DataFrame): The DataFrame to be visualized as a table.
        config (PlotChartConfig): Configuration object for saving the image.
        """
        self.df = df
        self.config = config

        logging.info(f"Image will be saved as {self.config.image_filename}")

    def create_table_image(self, width_factors=None, show_image=False, dpi=600):
        """
        Creates an image of the DataFrame rendered as a table and saves or displays it.

        Parameters:
        width_factors (dict, optional): A dictionary specifying width factors for each column.
        show_image (bool, optional): Whether to display the image or save it.
        dpi (int, optional): The DPI (dots per inch) for saving the image. Default is 500.

        Returns:
        io.BytesIO: The in-memory image object.
        """
        try:
            logging.info(f"DataFrame shape before creating image: {self.df.shape}")
            logging.info(f"DataFrame content:\n{self.df.head()}")

            # Create a figure and axis for the plot
            fig, ax = plt.subplots(figsize=(25, 15))  # Adjust size accordingly

            # Hide axes
            ax.xaxis.set_visible(False)
            ax.yaxis.set_visible(False)
            ax.set_frame_on(False)

            # Render the DataFrame as a table
            tbl = ax.table(cellText=self.df.values, colLabels=self.df.columns, cellLoc='center', loc='center')

            # Style the header row
            tbl.auto_set_font_size(False)
            tbl.set_fontsize(10)
            tbl.scale(1, 2)  # Adjust scaling if needed

            # Set colors for headers
            for key, cell in tbl.get_celld().items():
                if key[0] == 0:  # Header row
                    cell.set_text_props(weight='bold', color='black')
                    cell.set_facecolor('yellow')

            # Dynamically adjust column width
            if width_factors is None:
                width_factors = {col: 1.5 for col in self.df.columns}  # Default factor if none provided

            for col in self.df.columns:
                col_idx = self.df.columns.get_loc(col)
                # Determine max character length per column
                max_width = max([len(str(item)) for item in self.df[col]]) * width_factors.get(col, 1.5) * 0.004
                for key, cell in tbl.get_celld().items():
                    if key[1] == col_idx:
                        cell.set_width(max_width)

            # Save the plot as an image using BytesIO
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=dpi)  # High DPI for better quality
            buf.seek(0)

            logging.info("Image created in memory.")

            plt.close(fig)  # Close the figure to free memory

            return buf  # Return the in-memory image buffer

        except Exception as e:
            logging.error(f"An error occurred while creating the table image: {str(e)}", exc_info=True)
            raise CustomException(e)
