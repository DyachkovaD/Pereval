from django.db import transaction
from django.shortcuts import render
from django.utils import timezone
from pyexpat.errors import messages
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from adding.models import Pereval, Users, Coords, Image, Status
from adding.serializers import PerevalSerializer


class PerevalView(APIView):

    def get(self, request: object, **kwargs) -> (Response):
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

    def delete(self, request: object, **kwargs) -> (Response):
        id = kwargs.get("id", None)
        try:
            snippet = Pereval.objects.get(id=id)
            snippet.delete()
            snippet = PerevalSerializer(snippet)
        except Pereval.DoesNotExist:
            return Response({"message": "Перевал не найден"}, status=status.HTTP_404_NOT_FOUND)
        return Response(snippet)

    def patch(self, request: object, **kwargs):
        id = kwargs.get("id")
        data = request.data.copy()

        if not id:
            return Response({"message": "Не передан id"}, status=status.HTTP_400_BAD_REQUEST)
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

    def post(self, request: object) -> (Response):
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
                        image = Image.objects.create(img=image["data"], title=image['title'])
                        image.pereval = serializer.instance
                        image.save()
                return Response({"status": 200, "message": "перевал успешно создан", "id": serializer.instance.id})
            return Response(serializer.errors)
