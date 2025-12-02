from django.shortcuts import render

# Create your views here.
def hotlines_page(request):
    return render(request, "hotlines/hotlines.html")
