import logging
import sys


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Use the root logger or a named logger that propagates to root
    logger = logging.getLogger("ocrpolish")
    logger.setLevel(level)
    
    # Clear existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    # Ensure it doesn't propagate to a root handler that might be configured elsewhere
    logger.propagate = False
    
    return logger

def get_logger() -> logging.Logger:
    """Get the application logger."""
    return logging.getLogger("ocrpolish")
