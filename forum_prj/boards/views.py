from django.shortcuts import render, get_object_or_404,redirect
from .models import Board,Topic,Post
from django.http import Http404
from django.contrib.auth.models import User



def home(request):
    boards = Board.objects.all()
    return render(request, 'boards/home.html', {'boards': boards})

def board_topics(request, pk):
    board = get_object_or_404(Board, pk=pk)  # Retrieve the board
    topics = board.topics.all()  # Get all topics related to this board
    return render(request, 'boards/topics.html', {'board': board, 'topics': topics})

def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        if subject and message:  
            topic = Topic.objects.create(board=board, subject=subject, starter=request.user)
            Post.objects.create(topic=topic, message=message, created_by=request.user)
            return redirect('board_topics', pk=board.pk) 
    return render(request, 'boards/new_topic.html', {'board': board})