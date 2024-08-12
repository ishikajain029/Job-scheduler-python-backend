from bson.errors import InvalidId
from bson import ObjectId
from apscheduler.triggers.cron import CronTrigger

def is_valid_object_id(id_str):
    """
    Checks if the provided string is a valid ObjectId.

    Args:
        id_str (str): The string to be validated as an ObjectId.

    Returns:
        bool: True if the string is a valid ObjectId, otherwise False.
    """
    try:
        ObjectId(id_str)
        return True
    except (InvalidId, TypeError):
        return False

def validate_cron_expression(cron_expression):
    """
    Validates a cron expression to ensure it can be parsed by APScheduler.

    Args:
        cron_expression (str): The cron expression to be validated.

    Returns:
        bool: True if the cron expression is valid, otherwise False.

    Raises:
        ValueError: If the cron expression is invalid.
    """
    try:
        CronTrigger.from_crontab(cron_expression)
        return True
    except ValueError:
        return False
    
def is_string(input_value):
    """
    Checks if the input value is a string.

    Args:
        input_value: The value to be checked.

    Returns:
        bool: True if the input value is a string, otherwise False.
    """
    return isinstance(input_value, str)
