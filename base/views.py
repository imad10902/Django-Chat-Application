from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.http import HttpResponse
from .models import Room, Topic, Message
from django.contrib.auth import authenticate, login, logout
from .forms import RoomForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User# table that stores user data

rooms = [
    {'id': 1, 'name': 'Learn Python!'},
    {'id': 2, 'name': 'Learn React!'},
    {'id': 3, 'name': 'Learn Angular!'},
]
# Q for better search with | and &
#the submission would come to the same url where the form is called
def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:#if i am logged in i should not be on login page by url too
        return redirect('home') 

    if request.method == 'POST':
        username = request.POST.get('username').lower()#getting username and password
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)#check if user exists
        except:
            messages.error(request, 'User doesnt exist.')
        
        user = authenticate(request, username=username, password=password)#either it errors or returns user with these credentials

        if user is not None:
            login(request, user)#session in our database is added
            return redirect('home')
        else:
            messages.error(request, 'Username and password doesnt exist')
    context= {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutPage(request):
    logout(request)
    return redirect('home')

def registerUser(request):
    form = UserCreationForm()
#form comes to same url after submission which sends the form if not specified
    if request.method == 'POST':
        form = UserCreationForm(request.POST) # form is filled with request object, remember form is send to for template then we need to do this step too
        if form.is_valid():
            user = form.save(commit = False) #we want created user immediately using commit
            user.username = user.username.lower()
            user.save()#now commit
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during resgitration')
    return render(request, 'base/login_register.html', {'form': form})

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''# q query is used to filter rooms and again render template with filtered rooms
    rooms = Room.objects.filter(topic_name__icontains= q)#all objects of Room table if all()
    topics = Topic.objects.all()
    context= {'rooms': rooms, 'topics': topics }
    return render(request, 'base/home.html', context)

def room(request, pk):#related to rooms, rooms themselves.
    room = None
    for i in rooms:
        room = Room.objects.get(id=pk)
        room_messages = room.message_set.all().order_by('-created')# load messages of this room, accessed from data table, using messages model
        participants = room.participants# load participants of respective rooms
        if request.method == 'POST':
            message = Message.objects.create(# save the message when url is reached after susbmission of message
                user = request.user,
                room= room,
                body= request.POST.get('body')
            )
            room.participants.add(request.user) #to add user in conversation 
    context = {'room': room, 'messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)

@login_required(login_url='/login')#create room option only appears if logged in
def createRoom(request):
    form = RoomForm() 
    if request.method == 'POST':
        form = RoomForm(request.POST)#form comes back data
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'base/room_form.html', context),
#passing req and context to html to render.
#from url is fetch or url is reached then url runs and because of that function in view runs. view has access to data(model) as well as template
#connecting model to what has to be returned
#Yes, when the user submits the form, the submission typically comes to the same URL that points to the createRoom view function.
@login_required(login_url='/login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)#accessing object in Room table from view
    form = RoomForm(instance=room)#pre filled with room values

    if request.user != room.host:
        return HttpResponse('You are not allowed here!')# so that anyone cannot change anyone's data

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)#saving to form, form instance was sent too to style the template
        if form.is_valid():
            form.save()
    context = {'form': form}
    return render(request, 'base/room_form.html', context)
@login_required(login_url='/login')
def deleteRoom(request, pk):
    room = Room.objects.get(id = pk)
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})#twop layered first sends anything to form then form submits to save url and handle it
#it is important to make the form using inbuilt modules and provide metadeta using tables. then use these forms
#only one thing can be returned
#template are not manupulated inside function

@login_required(login_url='/login')
def deleteMessage(request, pk):
    message = Message.objects.get(id = pk)#accesing messages data table to reach message that has id

    if request.user != message.user:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})