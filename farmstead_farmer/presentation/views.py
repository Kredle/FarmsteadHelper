from django.shortcuts import render


def react_shell(request):
    return render(request, 'api/mainpage.html')
