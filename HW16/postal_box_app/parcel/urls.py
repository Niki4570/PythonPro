from xml.etree.ElementInclude import include

from django.urls import path

import parcel.views
import post_machine.views


urlpatterns = [
    path('', parcel.views.all_parcels_view),
    path('<parcel_id>', parcel.views.one_parcel_view),
]
