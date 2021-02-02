import pytest

from fixtures.notification_fixture import smtp_connection
from fixtures.uaa_fixture import (
    uaa_authenticated,
    uaa_deactivate_multiple_users,
    uaa_deactivate_user,
    uaa_deactivate_multiple_pages_of_users,
    uaa_list_users_multiple_pages,
    uaa_list_expiring_users,
    uaa_unauthorized,
)
from fixtures.config import authenticated_response, base_url
