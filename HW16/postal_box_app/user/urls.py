from django.urls import path
from . import views


urlpatterns = [
    path('<user_id>', views.user_page),
]
