from django.urls import path
from .views import TeacherView, MapView

app_name = "teacher"
urlpatterns = [
    path("info/all", TeacherView.as_view(action="all"), name="all"),
    path("info", TeacherView.as_view(action="name"), name="info"),
    path("map", MapView.as_view(), name="map"),
]
