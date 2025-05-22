from django.urls import path

from adding.views import PerevalView, upload_img



urlpatterns = [
    path("pereval/", PerevalView.as_view()),
    path("upload_img/", upload_img)
]
