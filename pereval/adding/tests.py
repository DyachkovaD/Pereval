import pytest
from django.urls import reverse
from rest_framework import status

from adding.models import *


@pytest.mark.django_db
class TestPerevalView:
    def test_get_pereval_list(self, api_client, create_pereval):
        url = reverse('pereval-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['title'] == "Existing Pereval"

    def test_get_pereval_by_id(self, api_client, create_pereval):
        url = reverse('pereval-detail', kwargs={'id': create_pereval.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == "Existing Pereval"

    def test_get_pereval_by_nonexistent_id(self, api_client):
        url = reverse('pereval-detail', kwargs={'id': 999})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['message'] == "Перевал не найден"

    def test_get_pereval_by_user_email(self, api_client, create_pereval, create_user):
        url = reverse('pereval-list') + f"?user__email={create_user.email}"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['title'] == "Existing Pereval"

    def test_create_pereval_success(self, api_client, pereval_data):
        url = reverse('pereval-list')
        response = api_client.post(url, data=pereval_data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == "перевал успешно создан"
        assert Pereval.objects.count() == 1
        assert Users.objects.count() == 1
        assert Coords.objects.count() == 1
        assert Image.objects.count() == 1

    def test_create_pereval_missing_title(self, api_client, pereval_data):
        pereval_data.pop('title')
        url = reverse('pereval-list')
        response = api_client.post(url, data=pereval_data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.data['message']


    def test_update_pereval_success(self, api_client, create_pereval):
        url = reverse('pereval-detail', kwargs={'id': create_pereval.id})
        update_data = {
            "title": "Updated Pereval",
            "coords": {
                "latitude": "46.3842",
                "longitude": "8.1525",
                "height": "1300"
            }
        }
        response = api_client.patch(url, data=update_data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == "Успешно обновлено"
        create_pereval.refresh_from_db()
        assert create_pereval.title == "Updated Pereval"
        assert str(create_pereval.coord_id.latitude) == "46.3842"

    def test_update_pereval_change_user(self, api_client, create_pereval, user_data):
        url = reverse('pereval-detail', kwargs={'id': create_pereval.id})
        update_data = {
            "user": user_data
        }
        response = api_client.patch(url, data=update_data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['message'] == "Нельзя изменять пользователя, добавившего запись"

    def test_update_pereval_not_new_status(self, api_client, create_pereval):
        create_pereval.status = Status.ACC
        create_pereval.save()

        url = reverse('pereval-detail', kwargs={'id': create_pereval.id})
        update_data = {
            "title": "Updated Pereval"
        }
        response = api_client.patch(url, data=update_data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['message'] == "Нельзя редактировать перевал, проверенный модератором"

    def test_update_pereval_nonexistent_id(self, api_client):
        url = reverse('pereval-detail', kwargs={'id': 999})
        update_data = {
            "title": "Updated Pereval"
        }
        response = api_client.patch(url, data=update_data, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['message'] == "Перевал не найден"

    def test_delete_pereval_success(self, api_client, create_pereval):
        url = reverse('pereval-detail', kwargs={'id': create_pereval.id})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_200_OK
        assert Pereval.objects.count() == 0

    def test_delete_pereval_nonexistent_id(self, api_client):
        url = reverse('pereval-detail', kwargs={'id': 999})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['message'] == "Перевал не найден"