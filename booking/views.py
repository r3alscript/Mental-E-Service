from django.shortcuts import render
from authorization.models import Psychologist

def psychologists_list(request):
    psychologists = Psychologist.objects.all()
    return render(request, 'booking/psychologists_list.html', {
        'psychologists': psychologists
    })

def booking_page(request):
    return render(request, 'booking/booking_page.html')

def calendar_page(request):
    return render(request, 'booking/calendar_page.html')