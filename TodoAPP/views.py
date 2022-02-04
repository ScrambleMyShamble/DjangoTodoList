from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def home(request):  # HOME PAGE
    return render(request, 'todoapp/home.html')


def signupuser(request):  # REGISTRATION

    if request.method == 'GET':
        return render(request, 'todoapp/signupuser.html', {'form': UserCreationForm()})

    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')

            except IntegrityError:
                return render(request, 'todoapp/signupuser.html',
                              {'form': UserCreationForm(), 'error': 'This user already exists'})

        else:
            return render(request, 'todoapp/signupuser.html',
                          {'form': UserCreationForm(), 'error': 'Password did not match'})


@login_required
def currenttodos(request):  # NOT FINISHED TASKS
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)

    return render(request, 'todoapp/currenttodos.html', {'todos': todos})


@login_required
def logoutuser(request):  # LOGOUT
    if request.method == 'POST':
        logout(request)
        return redirect('home')


def loginuser(request):  # ENTER
    if request.method == 'GET':
        return render(request, 'todoapp/loginuser.html', {'form': AuthenticationForm()})

    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todoapp/loginuser.html',
                          {'form': AuthenticationForm(), 'error': 'Password didnt match login'})
        else:
            login(request, user)
            return redirect('currenttodos')


@login_required
def createtodo(request):  # CREATE TODOS
    if request.method == 'GET':
        return render(request, 'todoapp/createtodo.html', {'form': TodoForm()})
    else:
        form = TodoForm(request.POST)
        newtodo = form.save(commit=False)
        newtodo.user = request.user
        newtodo.save()
        return redirect('currenttodos')


@login_required
def viewtodo(request, todo_pk):  # LOOK TODOS
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todoapp/viewtodo.html', {'todo': todo, 'form': form})
    else:
        form = TodoForm(request.POST, instance=todo)
        form.save()
        return redirect('currenttodos')


@login_required
def completetodo(request, todo_pk):  # CHECK COMPLETE TASKS
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')


@login_required
def deletetodo(request, todo_pk):  # DELETE TASKS
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodos')


@login_required
def completedview(request):  # FINISHED TASKS
    todo_comp = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'todoapp/completed.html', {'todo': todo_comp})
