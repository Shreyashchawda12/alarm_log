import sys
from src.logger import logging

def error_message_detail(error, error_detail: sys):
    """
    Extract detailed error message from error_detail.

    Parameters:
    error (Exception): The original exception.
    error_detail (sys): sys.exc_info() that contains error details (type, value, traceback).
    
    Returns:
    str: Formatted error message with the script name, line number, and error details.
    """
    _, _, exc_tb = error_detail.exc_info()
    
    if exc_tb is not None:
        file_name = exc_tb.tb_frame.f_code.co_filename
        line_number = exc_tb.tb_lineno
    else:
        file_name = "Unknown"
        line_number = "Unknown"
    
    error_message = (
        f"Error occurred in python script name [{file_name}] line number [{line_number}] "
        f"error message [{str(error)}]"
    )
    
    return error_message

class CustomException(Exception):
    def __init__(self, error_message, error_detail: sys):
        super().__init__(error_message)
        self.error_message = error_message_detail(error_message, error_detail=error_detail)

    def __str__(self):
        return self.error_message


if __name__ == "__main__":
    logging.info("Logging has started")

    try:
        a = 1 / 0  # Deliberate division by zero error to trigger exception
    except Exception as e:
        logging.error("Division by zero occurred") 
        raise CustomException(e, sys)
