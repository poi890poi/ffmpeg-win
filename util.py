import time
import logging
import logging.handlers
import os
import inspect


# Define log file settings
LOG_FILE = "app.log"
LOG_DIR = "logs"

def duration_to_seconds(duration):
    try:
        # Split the duration into hours, minutes, and seconds
        hours, minutes, seconds = duration.split(":")
        # Convert hours and minutes to integers, and seconds to a float to support optional decimals
        hours = int(hours)
        minutes = int(minutes)
        seconds = float(seconds)

        # Calculate the total number of seconds
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return int(total_seconds)
    except ValueError:
        ...
    try:
        return int(duration)
    except ValueError:
        print("Invalid format. Please use HH:MM:SS, HH:MM:SS.sss, or seconds")
        return None

def convert_seconds_to_hhmmss(duration):
    """Convert a duration in seconds to HH:MM:SS format."""
    hours = int(duration // 3600)
    minutes = int((duration % 3600) // 60)
    seconds = int(duration % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def convert_epoch_to_hhmmss(epoch_time):
    """Convert epoch time (absolute seconds) to HH:MM:SS format."""
    local_time = time.localtime(epoch_time)  # Convert epoch to local time
    return time.strftime("%H:%M:%S", local_time)

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)
log_path = os.path.join(LOG_DIR, LOG_FILE)

# Create a logger
def get_logger(name):
    """Returns a logger configured for both console and rotating file logging."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create a formatter that includes timestamp, filename, and line number
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(log_path, maxBytes=5*1024*1024, backupCount=3)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

class LoggerWriter:
    """Redirects print statements to a logger with correct file and line info."""
    def __init__(self, logger, level=logging.INFO):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.strip():  # Ignore empty lines
            frame = inspect.currentframe().f_back  # Get previous stack frame
            caller_filename = frame.f_code.co_filename
            caller_lineno = frame.f_lineno
            self.logger.log(self.level, (f"{caller_filename}:{caller_lineno}"
                            f" - {message.strip()}"))

    def flush(self):
        pass  # Required for compatibility with sys.stdout