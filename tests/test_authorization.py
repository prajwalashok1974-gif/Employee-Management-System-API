import pytest
from fastapi import HTTPException

from app.models import User
from app.routes.auth import require_admin_or_hr


@pytest.mark.parametrize("role", ["admin", "hr"])
def test_admin_and_hr_are_authorized_for_management(role):
    user = User(role=role)

    assert require_admin_or_hr(current_user=user) is user


def test_employee_is_forbidden_from_management_operations():
    user = User(role="employee")

    with pytest.raises(HTTPException) as exc_info:
        require_admin_or_hr(current_user=user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Administrator or HR access required"
