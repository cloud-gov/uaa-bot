import pytest

from fixtures.uaa_fixture import (
    uaa_authenticated,
    uaa_list_expiring_users,
    uaa_unauthorized,
)
from fixtures.config import authenticated_response, base_url
