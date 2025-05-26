from django.urls import path

from adding.views import PerevalView



urlpatterns = [
    path("submitData/", PerevalView.as_view()),
    path("submitData/<int:id>", PerevalView.as_view()),
]
