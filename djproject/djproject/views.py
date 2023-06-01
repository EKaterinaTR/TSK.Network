from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required

from djproject.forms import RegistrationForm, AuthForm, GraphPointListForm
from djproject.models import VKUser, StateGraph
from djproject.neo4j_query import Neo4JQuery
from djproject.vk_friends import FriendsLoader
from djproject.vk_utils import get_user_id

User = get_user_model()


@login_required
def main_view(request):
    return render(request, "main.html", {})


@login_required
def graphtop_view(request, algorithm='all'):
    form = GraphPointListForm()
    if request.method == 'POST' and request.POST.get('vk_id') is not None:
        form = GraphPointListForm(data=request.POST)
        real_vk_id = get_user_id(token=request.user.vkuser.vk_key, name_to_resolve=form.cleaned_data['vk_id'])
        FriendsLoader().run(user_id=real_vk_id, token=request.user.vkuser.vk_key, depth=1, graph_owner_id=request.user.id,
                            followers=False)
        neo4j = Neo4JQuery(graph_owner_id=request.user.id)
        if(algorithm == 'page_rank'):
            neo4j.page_rank()
            points = neo4j.get_nodes()
        elif(algorithm == 'hits'):
            neo4j.hits()
            points = neo4j.get_nodes()
        else:
            points = neo4j.get_nodes()
    else:
        points = []
    return render(request, "graphtop.html", {"form": form,'points': points})


@login_required
def graphtopmenu_view(request):
    form = GraphPointListForm()
    alg=0
    if request.method == 'GET' and request.GET.get('vk_id') is not None:
        form = GraphPointListForm(data=request.GET)
        real_vk_id = get_user_id(token=request.user.vkuser.vk_key, name_to_resolve=form.data['vk_id'])
        print(real_vk_id)
        FriendsLoader().run(user_id=real_vk_id, token=request.user.vkuser.vk_key, depth=1,
                            graph_owner_id=request.user.id,
                            followers=False)
        neo4j = Neo4JQuery(graph_owner_id=request.user.id)
        if (form.data['algorithm'][0] == '2'):
            alg = 2
            neo4j.page_rank()
            points = neo4j.get_nodes()
        elif (form.data['algorithm'][0] == '3'):
            alg = 3
            neo4j.hits()
            points = neo4j.get_nodes()
        else:
            points = neo4j.get_nodes()
    else:
        points = []
    print('all')
    form = GraphPointListForm()
    return render(request, "graphtopmenu.html", {"form": form, 'points': points, 'alg':alg})


def registration_view(request):
    form = RegistrationForm()
    is_success = False
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            user = User(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
            )
            vk_user = VKUser(user=user,
                             vk_key=form.cleaned_data['vk_key'])
            state_graph = StateGraph(user=user)
            user.set_password(form.cleaned_data['password'])
            user.save()
            vk_user.save()
            state_graph.save()
            is_success = True
    return render(request, "registration.html", {
        "form": form, "is_success": is_success
    })


def auth_view(request):
    form = AuthForm()
    if request.method == 'POST':
        form = AuthForm(data=request.POST)
        if form.is_valid():
            user = authenticate(**form.cleaned_data)
            if user is None:
                form.add_error(None, "Введены неверные данные")
            else:
                login(request, user)
                return redirect("main")
    return render(request, "auth.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("main")
