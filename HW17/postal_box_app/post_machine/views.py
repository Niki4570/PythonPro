from django.http import HttpResponse
from django.shortcuts import render
from . import models


def all_machines(request):
    post_machines = models.PostMachine.objects.all()
    return render(request, 'all_machines.html', context={'boxes': post_machines})

def post_machine_info(request, machine_id):
    post_machine = models.PostMachine.objects.get(pk=machine_id)
    lockers = models.Locker.objects.filter(post_machine_id=machine_id)
    return render(request, 'one_machine.html', {'box': post_machine, 'lockers': lockers})

def lockers_info(request, machine_id, locker_id):
    one_postmachine = models.PostMachine.objects.get(id=machine_id)
    postmachine_lockers = models.Locker.objects.filter(post_machine=one_postmachine)
    one_locker = models.Locker.objects.get(pk=locker_id)

    return HttpResponse("Locker Info")
