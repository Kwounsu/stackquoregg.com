from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.paginator import Paginator
from pusher import Pusher

from . import models
from . import forms

import pusher
pusher_client = pusher.Pusher(
  app_id='905115',
  key='47917f39c6cb18036d35',
  secret='f44dead560c494918a01',
  cluster='us3',
  ssl=True
)
pusher_client.trigger('my-channel', 'my-event', {'message': 'hello world'})

@csrf_exempt
@login_required(login_url='/login/')
def chatting(request, room):
    data = models.Conversation.objects.filter(status=room)
    data = [{'name': person.user.username, 'status': person.status, 'message': person.message, 'id': person.id} for person in data]
    context = {
        "title":"Stack Quoregg",
        "data":data,
        "room":room
    }
    return render(request, 'tutor_chat.html', context=context)

# instantiate pusher
pusher = Pusher(app_id=u'905115', key=u'47917f39c6cb18036d35', secret=u'f44dead560c494918a01', cluster=u'us3')
#use the csrf_exempt decorator to exempt this function from csrf checks
@csrf_exempt
def broadcast(request):
    # collect the message from the post parameters, and save to the database
    message = models.Conversation(message=request.POST.get('message', ''), status='', user=request.user);
    message.save();
    # create an dictionary from the message instance so we can send only required details to pusher
    message = {'name': message.user.username, 'status': message.status, 'message': message.message, 'id': message.id}
    #trigger the message, channel and event to pusher
    pusher.trigger(u'a_channel', u'an_event', message)
    # return a json response of the broadcasted message
    return JsonResponse(message, safe=False)

#return all conversations in the database
def conversations(request):
    data = models.Conversation.objects.all()
    # loop through the data and create a new list from them. Alternatively, we can serialize the whole object and send the serialized response 
    data = [{'name': person.user.username, 'status': person.status, 'message': person.message, 'id': person.id} for person in data]
    # return a json response of the broadcasted messgae
    return JsonResponse(data, safe=False)

#use the csrf_exempt decorator to exempt this function from csrf checks
@csrf_exempt
def delivered(request, id):
    message = models.Conversation.objects.get(pk=id);
    # verify it is not the same user who sent the message that wants to trigger a delivered event
    if request.user.id != message.user.id:
        socket_id = request.POST.get('socket_id', '')
        message.status = 'Delivered';
        message.save();
        message = {'name': message.user.username, 'status': message.status, 'message': message.message, 'id': message.id}
        pusher.trigger(u'a_channel', u'delivered_message', message, socket_id)
        return HttpResponse('ok');
    else:
        return HttpResponse('Awaiting Delivery');

# Create your views here.
def index(request):
    context = {
        "title":"Stack Quoregg",
        "variable":"Welcome to the Stack Quoregg!",
        "variable2":"Learn and grow with Stack Queoregg",
    }
    return render(request, "index.html", context=context)

@csrf_exempt
@login_required(login_url='/login/')
def suggestions_view(request):
    if request.method == "GET":
        suggestion_query = models.Suggestion.objects.all().order_by('-created_on')
        suggestion_list = {"suggestions":[]}
        for s_q in suggestion_query:
            comment_query = models.Comment.objects.filter(suggestion=s_q)
            comment_list = []
            for c_q in comment_query:
                can_delete=False
                if request.user == c_q.author:
                    can_delete=True
                comment_list += [{
                "comment":c_q.comment,
                "author":c_q.author.username,
                "created_on":c_q.created_on,
                "id":c_q.id,
                "delete":can_delete
                }]
            url = ""
            if not str(s_q.image)=="":
                url=s_q.image.url
            suggestion_list["suggestions"] += [{
                "id":s_q.id,
                "suggestion":s_q.suggestion,
                # "sugg_description":s_q.sugg_description,
                "author":s_q.author.username,
                "created_on":s_q.created_on,
                "comments":comment_list,
                "image":url,
                "image_description":s_q.image_description
                }]
        return JsonResponse(suggestion_list)
    return HttpResponse("Unsupported HTTP Method")

@login_required(login_url='/login/')
def suggestion_form_view(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            form_instance = forms.SuggestionForm(request.POST, request.FILES)
            if form_instance.is_valid():
                new_sugge = form_instance.save(request=request)
                return redirect("/qna/")
        else:
            return redirect("/qna/")
    else:
        form_instance = forms.SuggestionForm()
    context = {
        "title":"Stack Quoregg",
        "form":form_instance
    }
    return render(request, "suggestion.html", context=context)

@login_required(login_url='/login/')
def comments_view(request, instance_id, delete=0):
    if delete==1:
        print("Should delete the comment here")
        instance = models.Comment.objects.get(id=instance_id)
        if request.user == instance.author:
            instance.delete()
        return redirect("/qna/")
    if request.method == "POST":
        if request.user.is_authenticated:
            form_instance = forms.CommentForm(request.POST)
            if form_instance.is_valid():
                new_comm = form_instance.save(request=request, sugg_id=instance_id)
                return redirect("/answer/"+ str(instance_id) + "/")
        else:
            form_instance = forms.CommentForm()
    else:
        form_instance = forms.CommentForm()
    question = models.Suggestion.objects.get(id=instance_id)
    answers = models.Comment.objects.filter(suggestion=question).order_by('-upvote')
    context = {
        "title":"Stack Quoregg",
        "form":form_instance,
        "sugg_id":instance_id,
        "quest":question,
        "answer_list":answers
    }
    return render(request, "comment.html", context=context)

def upvote(request, comm_id):
    comm = models.Comment.objects.get(id=comm_id)
    comm.upvote += 1
    comm.save()
    return redirect("/answer/"+ str(comm.suggestion.id) + "/")

def logout_view(request):
    logout(request)
    return redirect("/login/")

def register(request):
    if request.method == "POST":
        form_instance = forms.RegistrationForm(request.POST)
        if form_instance.is_valid():
            form_instance.save()
            return redirect("/login/")
    else:
        form_instance = forms.RegistrationForm()
    context = {
        "form":form_instance,
    }
    return render(request, "registration/register.html", context=context)

def about(request):
    context = {
        "title":"Stack Quoregg",
    }
    return render(request, 'about.html', context)

@login_required(login_url='/login/')
def qna(request, page=0):
    suggs = models.Suggestion.objects.all().order_by('-created_on')
    paginator = Paginator(suggs, 4)
    page = request.GET.get('page')
    suggs = paginator.get_page(page)
    totalQ = models.Suggestion.objects.all().count()
    context = {
        "title":"Stack Quoregg",
        "suggs":suggs,
        "page":page,
        "paginator":paginator,
        "totalQ":totalQ,
    }
    return render(request, 'qna.html', context=context)

@login_required(login_url='/login/')
def tutor(request, page=0, delete=0):
    if delete==1:
        instance = models.Tutor.objects.get(author=request.user)
        if request.user == instance.author:
            instance.delete()
        return redirect("/tutor/")
    tutors = models.Tutor.objects.all()
    paginator = Paginator(tutors, 5)
    page = request.GET.get('page')
    tutors = paginator.get_page(page)
    try:
        registered = True
        models.Tutor.objects.get(author=request.user)
    except:
        registered = False
    context = {
        "title":"Stack Quoregg",
        "tutors":tutors,
        "page":page,
        "paginator":paginator,
        "registered":registered,
    }
    return render(request, 'tutor.html', context=context)

@login_required(login_url='/login/')
def tutor_form_view(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            form_instance = forms.TutorForm(request.POST, request.FILES)
            if form_instance.is_valid():
                new_tutor = form_instance.save(request=request)
                return redirect("/tutor/")
        else:
            return redirect("/tutor/")
    else:
        form_instance = forms.TutorForm()
    context = {
        "title":"Stack Quoregg",
        "form":form_instance
    }
    return render(request, "tutorForm.html", context=context)

@login_required(login_url='/login/')
def search(request):
    br = models.Suggestion.objects.all().order_by('-created_on')
    b = request.GET.get('b','')
    if b:
        br = br.filter(suggestion__icontains=b) | br.filter(category__icontains=b)
    paginator = Paginator(br, 4)
    page = request.GET.get('page')
    br = paginator.get_page(page)
    context = {
        "title":"Stack Quoregg",
        "search":br,
        "b":b,
        "page":page,
        "paginator":paginator,
    }
    return render(request, 'search.html', context)

@login_required(login_url='/login/')
def searchTutor(request):
    br = models.Tutor.objects.all()
    b = request.GET.get('b','')
    if b:
        br = br.filter(category__icontains=b)
    paginator = Paginator(br, 5)
    page = request.GET.get('page')
    br = paginator.get_page(page)
    context = {
        "title":"Stack Quoregg",
        "search":br,
        "b":b,
        "page":page,
        "paginator":paginator,
    }
    return render(request, 'searchTutor.html', context)