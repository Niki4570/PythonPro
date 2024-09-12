from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def all_parcels_view(request):
    return HttpResponse("All Parcels View")

def one_parcel_view(request, parcel_id):
    return HttpResponse("One Parcel View")
