from django.shortcuts import render, get_object_or_404, redirect
from .models import Board, Topic, Post
from django.contrib.auth.models import User
from .forms import NewTopicForm, PostForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import ListView, UpdateView
from django.urls import reverse_lazy


class BoardListView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'boards/home.html'


class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'boards/topics.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return queryset


# View for creating a new topic in a board
@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()

            # Automatically create the first post for the topic
            Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )

            return redirect('topic_posts', pk=pk, topic_pk=topic.pk)  # Ensure this URL name exists in your urls.py
    else:
        form = NewTopicForm()
    return render(request, 'boards/new_topic.html', {'board': board, 'form': form})


# View for listing posts within a topic, with pagination
class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'boards/topic_posts.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        session_key = 'viewed_topic_{}'.format(self.topic.pk)
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True

        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset


# View for replying to a topic
@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_updated = timezone.now()
            topic.save()

            return redirect('topic_posts', pk=pk, topic_pk=topic_pk)
    else:
        form = PostForm()
    return render(request, 'boards/reply_topic.html', {'topic': topic, 'form': form})


# View for updating/editing a post
@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message',)
    template_name = 'boards/edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)


from django. contrib.auth.signals import user_logged_in
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.cache import cache

@receiver (user_logged_in, sender=User)
def login_success (sender, request, user,**kwargs) :
    ct = cache-get ('count', 0, version=user.pk)
    newcount = ct + 1
    cache.set( 'count', newcount, 60*60*24, version=user.pk)
    print(user.pk)