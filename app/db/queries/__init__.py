"""Database queries package."""

from .users import (
    get_user_by_tg_id,
    get_user_by_telegram_id,
    create_user,
    update_user_settings,
    update_user_direction,
    get_active_users,
    get_users_by_direction,
    delete_user
)

from .directions import (
    get_all_directions,
    get_directions_by_course,
    get_direction_by_id,
    create_direction,
    update_direction,
    delete_direction
)

from .pairs import (
    get_pairs_by_direction_and_day,
    get_all_pairs,
    get_pair_by_id,
    create_pair,
    update_pair,
    delete_pair,
    get_pair_directions
)

__all__ = [
    # Users
    'get_user_by_tg_id',
    'get_user_by_telegram_id',
    'create_user',
    'update_user_settings',
    'update_user_direction',
    'get_active_users',
    'get_users_by_direction',
    'delete_user',
    # Directions
    'get_all_directions',
    'get_directions_by_course',
    'get_direction_by_id',
    'create_direction',
    'update_direction',
    'delete_direction',
    # Pairs
    'get_pairs_by_direction_and_day',
    'get_all_pairs',
    'get_pair_by_id',
    'create_pair',
    'update_pair',
    'delete_pair',
    'get_pair_directions'
]
