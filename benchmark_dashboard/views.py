from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from benchmark_dashboard.models import Poll
from benchmark_dashboard.models import Choice
from benchmark_dashboard.models import Task
from benchmark_dashboard.models import Server


def info(request):
    return HttpResponse("Benchmark Tools")


def index(request):
    return render(request, 'index.html')


def mongo_test(request):
    # poll = Poll.objects(question="What").first()
    # choice = Choice(choice_text="I'm at DjangoCon.fi", votes=23)
    # poll.choices.append(choice)
    # poll.save()
    # print poll.question
    # choice.save()
    Task(name="task1").save()
    tasks = Task.objects()

    # Server(company="abcdeeeeee").save()
    servers = Server.objects()
    print len(servers)
    return HttpResponse("the count of servers is : %s" % len(servers))

