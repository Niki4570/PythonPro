from django.urls import path
import parcel.views

urlpatterns = [
    path('', parcel.views.all_parcels_view, name='all_parcels'),
    path('<parcel_id>', parcel.views.one_parcel_view, name='parcel_info'),
]
