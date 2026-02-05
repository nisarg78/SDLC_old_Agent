"""
Logger Utility
Provides structured logging for the autonomous SDLC system.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str, log_file: Path = None, level=logging.INFO) -> logging.Logger:
    """
    Set up a logger with both file and console handlers.
    
    Args:
        name: Logger name
        log_file: Path to log file (optional)
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)-8s [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)-8s %(message)s'
    )
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler (DEBUG and above)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    return logger


class SDLCLogger:
    """Enhanced logger with structured logging capabilities"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.context = {}
    
    def set_context(self, **kwargs):
        """Set context variables that will be included in all log messages"""
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear all context variables"""
        self.context = {}
    
    def _format_message(self, message: str) -> str:
        """Format message with context"""
        if self.context:
            context_str = " ".join([f"{k}={v}" for k, v in self.context.items()])
            return f"{message} [{context_str}]"
        return message
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(self._format_message(message), extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(self._format_message(message), extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(self._format_message(message), extra=kwargs)
    
    def error(self, message: str, exc_info=False, **kwargs):
        """Log error message"""
        self.logger.error(self._format_message(message), exc_info=exc_info, extra=kwargs)
    
    def critical(self, message: str, exc_info=False, **kwargs):
        """Log critical message"""
        self.logger.critical(self._format_message(message), exc_info=exc_info, extra=kwargs)
    
    def phase_start(self, phase_name: str):
        """Log phase start"""
        self.logger.info("=" * 80)
        self.logger.info(f"PHASE START: {phase_name.upper()}")
        self.logger.info("=" * 80)
    
    def phase_end(self, phase_name: str, status: str = "completed"):
        """Log phase end"""
        self.logger.info("-" * 80)
        self.logger.info(f"PHASE {status.upper()}: {phase_name.upper()}")
        self.logger.info("-" * 80)
    
    def decision(self, decision: str, rationale: str = ""):
        """Log an autonomous decision"""
        self.logger.info(f"DECISION: {decision}")
        if rationale:
            self.logger.info(f"RATIONALE: {rationale}")
    
    def metric(self, name: str, value: any):
        """Log a metric"""
        self.logger.info(f"METRIC: {name} = {value}")
