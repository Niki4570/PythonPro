from django.http import HttpResponse

def all_machines(request):
    return HttpResponse("All Machines View")

def post_machine_info(request, machine_id):
    return HttpResponse("One Machine View")

def locker_info(request, machine_id, locker_id):
    return HttpResponse("Locker Info")
