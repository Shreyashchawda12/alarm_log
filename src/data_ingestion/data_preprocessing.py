import pandas as pd
import io
import matplotlib.pyplot as plt
import sys
import textwrap
from dataclasses import dataclass
from src.exception import CustomException
from src.logger import logging


@dataclass
class PlotChartConfig:
    image_filename: str = "Alarm.png"
    max_rows_per_image: int = 25   # 🔥 split large data


class PlotChart:
    def __init__(self, df: pd.DataFrame, config: PlotChartConfig = PlotChartConfig()):
        self.df = df.copy()
        self.config = config
        logging.info(f"Image will be saved as {self.config.image_filename}")

    def _wrap_text(self, text, width=20):
        """Wrap long text for better display"""
        return "\n".join(textwrap.wrap(str(text), width=width))

    def create_table_image(self, show_image=False, dpi=300):
        try:
            if self.df.empty:
                raise CustomException("DataFrame is empty. Cannot create table image.", sys)

            logging.info(f"Creating table image for {len(self.df)} rows")

            # 🔹 Limit rows (important for readability)
            df_display = self.df.head(self.config.max_rows_per_image).copy()

            # 🔹 Wrap long text
            for col in df_display.columns:
                df_display[col] = df_display[col].apply(lambda x: self._wrap_text(x, 25))

            # 🔹 Dynamic figure size
            rows, cols = df_display.shape
            fig_height = max(5, rows * 0.5)
            fig_width = max(10, cols * 2)

            fig, ax = plt.subplots(figsize=(fig_width, fig_height))
            ax.axis('off')

            # 🔹 Create table
            table = ax.table(
                cellText=df_display.values,
                colLabels=df_display.columns,
                cellLoc='center',
                loc='center'
            )

            table.auto_set_font_size(False)
            table.set_fontsize(9)

            # 🔹 Header styling
            for (row, col), cell in table.get_celld().items():
                if row == 0:
                    cell.set_text_props(weight='bold', color='white')
                    cell.set_facecolor('#40466e')  # dark header
                else:
                    cell.set_facecolor('#f5f5f5')

            # 🔹 Auto column width
            for col_idx in range(cols):
                max_len = max(
                    [len(str(x)) for x in df_display.iloc[:, col_idx]] + 
                    [len(df_display.columns[col_idx])]
                )
                width = min(max_len * 0.01, 0.3)
                for row_idx in range(rows + 1):
                    table[(row_idx, col_idx)].set_width(width)

            # 🔹 Save to memory buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=dpi)
            buf.seek(0)

            logging.info("Image created successfully")
            plt.close(fig)

            return buf

        except Exception as e:
            logging.error(f"Error creating table image: {str(e)}", exc_info=True)
            raise CustomException(e, sys)