from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required

from djproject.forms import RegistrationForm, AuthForm, GraphPointListForm, GroupForm
from djproject.graph_visualizer import GraphVisualizer
from djproject.models import VKUser, StateGraph
from djproject.neo4j_query import Neo4JQuery
from djproject.services import get_info_about_group, analyze_user
from djproject.vk_friends import FriendsLoader
from djproject.vk_utils import get_user_id

User = get_user_model()


@login_required
def main_view(request):
    return render(request, "main.html", {})

@login_required
def group_view(request):
    form = GroupForm()
    is_group = True
    if request.method == 'GET' and request.GET.get('group') is not None:
        form = GroupForm(data=request.GET)
        group = get_info_about_group(request.GET.get('group'), request.user.vkuser.vk_key)
        user_info = analyze_user(request.GET.get('group'), request.user.vkuser.vk_key)
    else:
        group = None
        user_info = None
        is_group = False
    return render(request, "group.html",
                  {"form": form, 'group': group,'is_group':is_group, 'user_info':user_info})


@login_required
def graphtopmenu_view(request):
    alg=0
    algorithm_path = None
    if request.method == 'GET' and request.GET.get('vk_id') is not None:
        form = GraphPointListForm(data=request.GET)
        real_vk_id = get_user_id(token=request.user.vkuser.vk_key, name_to_resolve=form.data['vk_id'])
        FriendsLoader().run(user_id=real_vk_id, token=request.user.vkuser.vk_key, depth=1,
                            graph_owner_id=request.user.id,
                            followers=False)
        neo4j = Neo4JQuery(graph_owner_id=request.user.id)
        if (form.data['algorithm'][0] == '2'):
            alg = 2
            neo4j.page_rank()
            points = sorted(neo4j.get_nodes(), key=lambda x: x['page_rank_result'], reverse=True)
        elif (form.data['algorithm'][0] == '3'):
            alg = 3
            neo4j.hits()
            points = neo4j.get_nodes()
        else:
            points = neo4j.get_nodes()

        # artemgur
        algorithm_dict = {2: 'page_rank', 3: 'hits'}
        algorithm = algorithm_dict.get(alg, None)
        GraphVisualizer(graph_owner_id=request.user.id, algorithm=algorithm).create_visualization()
        algorithm_path = f'pyvis_generated/graph_{request.user.id}.html'


    else:
        points = []
    print('all')
    form = GraphPointListForm()
    return render(request, "graphtopmenu.html", {"form": form, 'points': points, 'alg':alg, 'algorithm_path': algorithm_path})


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
