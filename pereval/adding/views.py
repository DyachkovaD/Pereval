import base64
from io import BytesIO
from tkinter.scrolledtext import example

from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import render
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from pyexpat.errors import messages
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from adding.models import Pereval, Users, Coords, Image, Status
from adding.serializers import PerevalSerializer


class PerevalView(APIView):

    @extend_schema(
        summary="Получить список всех перевалов",
        description="Получить список всех перевалов или конкретный перевал по ID",
        responses={
            200: PerevalSerializer,
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Перевал не найден",
                        value={"message": "Перевал не найден"}
                    ), ], ),
        }
    )
    def get(self, request: object, **kwargs) -> (Response):
        """
        Апи для получения перевалов
        """

        id = kwargs.get("id")
        user_email = request.GET.get("user__email")

        if id:
            try:
                snippet = Pereval.objects.get(id=id)
                serializer = PerevalSerializer(snippet)
                return Response(serializer.data)
            except Pereval.DoesNotExist:
                return Response({"message": "Перевал не найден"}, status=status.HTTP_404_NOT_FOUND)

        snippets = Pereval.objects.all()
        if user_email:
            snippets = snippets.filter(added_user__email=user_email)

        serializer = PerevalSerializer(snippets, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Удалить перевал",
        description="Удалить перевал по ID",
        responses={
            200: PerevalSerializer,
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Перевал не найден",
                        value={"message": "Перевал не найден"}
                    ), ], ),
        }
    )
    def delete(self, request: object, **kwargs) -> (Response):
        """
        Апи для удаления перевала
        """

        id = kwargs.get("id", None)
        try:
            snippet = Pereval.objects.get(id=id)
            snippet.delete()
            serializer = PerevalSerializer(snippet)
        except Pereval.DoesNotExist:
            return Response({"message": "Перевал не найден"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data)

    @extend_schema(
        summary="Изменить перевал",
        description="Изменить перевал по ID",
        request={
            "coords": {
                "latitude": "45.3842",
                "longitude": "7.1525",
                "height": "1250"
            },
            "level": {
                "winter": "2A"
            }
        },
        responses={
            200:OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Успешное изменение",
                        value={"message": "Успешно обновлено", "state": 1}
                    ), ], ),

            404:OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Перевал не найден",
                        value={"message": "Перевал не найден", "state": 0}
                    ), ], ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Изменение пользователя",
                        value={"message": "Нельзя изменять пользователя, добавившего запись", "state": 0}
                    ),
                    OpenApiExample(
                        "Не передан id",
                        value={"message": "Не передан id", "state": 0}
                    ),
                    OpenApiExample(
                        "Недоступен к редактированию",
                        value={"message": "Нельзя редактировать перевал, проверенный модератором", "state": 0}
                    ), ], ),
        }
    )
    def patch(self, request: object, **kwargs):
        """
        Апи для изменения перевала
        """
        id = kwargs.get("id")
        data = request.data.copy()

        if not id:
            return Response({"message": "Не передан id", "state": 0}, status=status.HTTP_400_BAD_REQUEST)
        if "user" in data:
            return Response({"message": "Нельзя изменять пользователя, добавившего запись", "state": 0},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            snippet = Pereval.objects.get(id=id)
            if snippet.status == Status.NEW:
                coords: dict = data.pop("coords")
                coords, created = Coords.objects.get_or_create(
                    **coords
                )
                data["coord_id"] = coords.id

                if "level" in data:
                    for season, level in data.pop("level").items():
                        data[season] = level

                images: list = data.pop("images", None)
                serializer = PerevalSerializer(instance=snippet, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    if images:
                        for image in images:
                            image = Image.objects.create(img=image["data"], title=image['title'])
                            image.pereval = serializer.instance
                            image.save()
                    return Response({"message": "Успешно обновлено", "state": 1})
                else:
                    return Response({"message": serializer.errors, "state": 0}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "Нельзя редактировать перевал, проверенный модератором", "state": 0},
                                status=status.HTTP_400_BAD_REQUEST)
        except Pereval.DoesNotExist:
            return Response({"message": "Перевал не найден", "state": 0}, status=status.HTTP_404_NOT_FOUND)


    @extend_schema(
        summary="Создать перевал",
        description="Создать перевал по ID",
        request=PerevalSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Успешное создание",
                        value={"status": 200, "message": "перевал успешно создан", "id": 1}
                    ), ], ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Ошибки сериализации",
                        value={"message": {"title": "Это обязательное поле"}, "status": 400},
                    ), ], ),
        }
    )
    def post(self, request: object) -> (Response):
        """
        Апи для создания перевала
        """
        data = request.data.copy()

        with transaction.atomic():
            user: dict = data.pop("user")
            user, created = Users.objects.get_or_create(
                email=user["email"],
                defaults={"email": user["email"], "name": user.get("name"),
                          "fam": user.get("fam"), "otc": user.get("otc"), "phone": user.get("phone")}
            )
            data["added_user"] = user.id

            coords: dict = data.pop("coords")
            coords, created = Coords.objects.get_or_create(
                **coords
            )
            data["coord_id"] = coords.id

            if "level" in data:
                for season, level in data.pop("level").items():
                    data[season] = level

            #   Как быть, если картинки нет? :с
            images: list = data.pop("images", None)

            serializer = PerevalSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                if images:
                    for image in images:
                        # Декодируем base64 в бинарные данные (если нужно сохранить файл)
                        decoded_data = base64.b64decode(image["data"])
                        Image.objects.create(img=decoded_data, title=image['title'], pereval=serializer.instance)

                return Response({"message": "перевал успешно создан", "id": serializer.instance.id, "status": 200})
            return Response({"message": serializer.errors, "status": 400}, status=status.HTTP_400_BAD_REQUEST)
