from django.shortcuts import render

def forum_main(request):
    return render(request, 'forumpage.html')

def discussion_detail(request):
    return render(request, 'discussion_detail.html')

def new_discussion(request):
    return render(request, 'create_discussion.html')