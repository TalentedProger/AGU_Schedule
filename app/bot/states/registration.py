"""
FSM States for bot registration flow.

Defines states for multi-step user registration process.
"""

from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    """States for user registration flow."""
    
    awaiting_name = State()       # Waiting for user's name
    awaiting_course = State()     # Waiting for course selection (1-4)
    awaiting_direction = State()  # Waiting for direction selection
    confirming = State()          # Confirming registration details
