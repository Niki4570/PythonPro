from django.http import HttpResponse
from . import models


def all_machines(request):
    return HttpResponse("All Machines View")

def post_machine_info(request, machine_id):
    post_machine_data = models.PostMachine.objects.filter(id=machine_id)
    post_machines_lockers = models.Locker.objects.filter(post_machine=machine_id)
    data_str = ', '.join([str(machine) for machine in post_machine_data])
    lockers_str = ', '.join([str(locker) for locker in post_machines_lockers])
    return HttpResponse(f"Post Machine: {data_str}<br>Lockers: {lockers_str}")

def lockers_info(request, machine_id, locker_id):
    one_postmachine = models.PostMachine.objects.get(id=machine_id)
    postmachine_lockers = models.Locker.objects.filter(post_machine=one_postmachine)
    one_locker = models.Locker.objects.get(pk=locker_id)

    return HttpResponse("Locker Info")
