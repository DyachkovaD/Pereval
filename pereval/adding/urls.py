from django.urls import path

from adding.views import PerevalView



urlpatterns = [
    path("submitData/", PerevalView.as_view(), name="pereval-list"),
    path("submitData/<int:id>", PerevalView.as_view(), name="pereval-detail"),
]
