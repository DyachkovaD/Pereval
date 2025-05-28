import pytest
from rest_framework.test import APIClient
from adding.models import *



@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        "email": "test@example.com",
        "name": "Test",
        "fam": "User",
        "otc": "Middle",
        "phone": "+79998887766"
    }


@pytest.fixture
def coords_data():
    return {
        "latitude": "45.3842",
        "longitude": "7.1525",
        "height": "1250"
    }


@pytest.fixture
def image_data():
    return {
        "data": "SGVsbG8gd29ybGQ=",
        "title": "Test Image"
    }


@pytest.fixture
def level_data():
    return {
        "winter": "2A",
        "summer": "1A",
        "autumn": "1B",
        "spring": "2B"
    }


@pytest.fixture
def pereval_data(user_data, coords_data, image_data, level_data):
    return {
        "title": "Test Pereval",
        "beauty_title": "Test Beauty Title",
        "other_titles": "Test Other Titles",
        "connect": "Test Connect",
        "add_time": "2021-09-22 13:18:13",
        "user": user_data,
        "coords": coords_data,
        "level": level_data,
        "images": [image_data]
    }


@pytest.fixture
def create_user(user_data):
    return Users.objects.create(**user_data)


@pytest.fixture
def create_pereval(create_user, coords_data):
    coords = Coords.objects.create(**coords_data)
    return Pereval.objects.create(
        title="Existing Pereval",
        beauty_title="Existing Beauty Title",
        other_titles="Existing Other Titles",
        connect="Existing Connect",
        add_time="2021-09-22 13:18:13",
        added_user=create_user,
        coord_id=coords,
        status=Status.NEW
    )
