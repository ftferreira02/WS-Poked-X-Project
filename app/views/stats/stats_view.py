from django.shortcuts import render

def stats_page(request):
    return render(request, 'stats.html')
