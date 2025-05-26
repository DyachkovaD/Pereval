from django.db import transaction
from django.shortcuts import render
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from adding.models import Pereval, Users, Coords, Image
from adding.serializers import PerevalSerializer



class PerevalView(APIView):

    def get(self, request: object, **kwargs) -> (Response):
        snippets = Pereval.objects.all()
        serializer = PerevalSerializer(snippets, many=True)

        return Response(serializer.data)

    def delete(self, request: object, **kwargs) -> (Response):
        id = kwargs.get("id", None)
        try:
            snippet = Pereval.objects.get(id=id)
            snippet.delete()
            snippet = PerevalSerializer(snippet)
        except Pereval.DoesNotExist:
            return Response({"details": "Перевал не найден"}, status=status.HTTP_404_NOT_FOUND)

        return Response(snippet)

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
                    images_ids: list = [img["data"] for img in images]
                    Image.objects.filter(id__in=images_ids).update(pereval=serializer.instance)
                return Response({"status": 200, "message": "перевал успешно создан", "id": serializer.instance.id})
            return Response(serializer.errors)
