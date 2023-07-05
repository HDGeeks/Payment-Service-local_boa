import requests
from utilities.identity import get_identity
import pytest


class TestGetIdentity(object):

    def test_get_identity_successfully(self):
        # Arrange
        user_id = "ZwA6ZuidRxOi3HGiy4aO5kHVx6v2"
        response = requests.get(
            f"https://kinideas-profile.calmgrass-743c6f7f.francecentral.azurecontainerapps.io/firebaseUser/{user_id}"
        )

        # Act
        result = get_identity(user_id)

        # Assert
        assert response.status_code == 200
        assert result == response.json()

        # Tests that the function returns a JSON object when a valid user ID is provided
    def test_valid_user_id(self):
        response = get_identity('user_id')
        assert isinstance(response, dict)




