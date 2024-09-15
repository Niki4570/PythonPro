from django.http import HttpResponse
from django.shortcuts import render
from . import  models
# Create your views here.

def all_parcels_view(request):
    user = request.user
    parcels = models.Parcel.objects.filter(recipient=user)
    return render(request, 'all_parcels.html', context={'parcels': parcels})

def one_parcel_view(request, parcel_id):
    parcel = models.Parcel.objects.get(pk=parcel_id)
    return render(request, 'one_parcel.html', {'parcel': parcel})
