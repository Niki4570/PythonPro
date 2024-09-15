from django.urls import path
from . import views


urlpatterns = [
    path('', views.all_machines, name='all_machines'),
    path('<machine_id>', views.post_machine_info, name='machine_info'),
    path('<machine_id>/<locker_id>', views.lockers_info, name='locker_info'),
]