"""
Utility Functions for DocuVision

This module provides helper functions for the Streamlit application,
including logging, UI elements, and data handling.
"""

import logging
import streamlit as st
from typing import Dict, Any

from config.settings import LOGGING_CONFIG, APP_CONFIG

def setup_logger() -> logging.Logger:
    """
    Set up and configure the application logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger("DocuVision")
    logger.setLevel(LOGGING_CONFIG['level'])

    # Create formatter
    formatter = logging.Formatter(LOGGING_CONFIG['format'])

    # Create file handler
    if LOGGING_CONFIG.get('log_file'):
        file_handler = logging.FileHandler(LOGGING_CONFIG['log_file'])
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Create stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger

def display_header(title: str = APP_CONFIG['page_title'], icon: str = APP_CONFIG['page_icon']):
    """
    Display the main application header in Streamlit.

    Args:
        title (str): The title to display.
        icon (str): The icon to display.
    """
    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout=APP_CONFIG.get('layout', 'wide'),
        initial_sidebar_state=APP_CONFIG.get('initial_sidebar_state', 'expanded')
    )
    st.title(f"{icon} {title}")
    st.markdown("Extract text from your documents with ease.")

def display_footer():
    """
    Display the application footer in Streamlit.
    """
    st.markdown("---")
    st.markdown(
        "Built with ❤️ using [Streamlit](https://streamlit.io), "
        "[Tesseract](https://github.com/tesseract-ocr/tesseract), "
        "and [OpenCV](https://opencv.org)."
    )
    st.markdown("Check out the source code on [GitHub](https://github.com/yourusername/docuvision-ocr)")


def get_app_config() -> Dict[str, Any]:
    """
    Get the application configuration.

    Returns:
        Dict[str, Any]: Application configuration dictionary.
    """
    return APP_CONFIG.copy()

def show_processing_error(e: Exception, logger: logging.Logger):
    """
    Display a user-friendly error message for processing failures.

    Args:
        e (Exception): The exception that occurred.
        logger (logging.Logger): The application logger.
    """
    logger.error(f"An error occurred during processing: {e}", exc_info=True)
    st.error(f"An unexpected error occurred: {e}")
    st.info("Please try again with a different file or contact support if the problem persists.") 