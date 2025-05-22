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
            other_titles = data.pop("other_titles", None)
            other_titles = [other_titles] if other_titles else []
            data["beauty_title"]: str = data.pop("beautyTitle", None)

            user: dict = data.pop("user")
            user, created = Users.objects.get_or_create(
                email=user["email"],
                defaults={"email": user["email"], "username": user["email"], "first_name": user.get("name"),
                          "last_name": user.get("fam"), "patronymic": user.get("otc"), "phone": user.get("phone")}
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
            if images:
                images_ids: list = [img["data"] for img in images]

            serializer = PerevalSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                serializer.instance.images.add(*images_ids)
                serializer.instance.other_titles.extend(other_titles)
                serializer.instance.save()

                return Response(serializer.data)
            return Response(serializer.errors)


@api_view(["POST"])
def upload_img(request):
    """ Апи для загрузки изображений в модель Image """

    img_data = request.FILES['image'].read()

    # Создаем изображение
    Image.objects.create(
        date_added=timezone.localtime(),
        img=img_data,
        title=request.data.get('title', '')
    )
    return Response({"message": "Изображение успешно загружено"})
