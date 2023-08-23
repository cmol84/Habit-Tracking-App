from enum import Enum


class Periodicity(Enum):
    """ An enumeration class representing the periodicity of a habit.
    Attributes:
        DAILY (str): Represents a habit that occurs every day.
        WEEKLY (str): Represents a habit that occurs every week.
        MONTHLY (str): Represents a habit that occurs every month."""
    DAILY = 'Every Day'
    WEEKLY = 'Every Week'
    MONTHLY = 'Every Month'
