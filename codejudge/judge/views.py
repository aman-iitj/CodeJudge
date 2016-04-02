#!/usr/bin/python

from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.conf import settings
from django.conf.urls.static import static
from judge.models import *
from datetime import *
import json
import socket
import requests
import random, string, os, subprocess

# Create your views here.

class Socket:

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def send(self, msg):
        sent = self.sock.send(msg)


def userLogin(request):
    try:
        if request.session['username']:
            return HttpResponseRedirect("/judge")
    except KeyError:
        context = RequestContext(request)
        error = False
        if request.method == 'POST' and request.is_ajax():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user != None:
                if user.is_authenticated():
                    login(request, user)
                    request.session['username']  = username
                    request.session['password']  = password
                    return HttpResponse(json.dumps({'errors': error}),content_type='application/json')
                else:
                    error = True
                    return HttpResponse(json.dumps({'errors': error}),content_type='application/json')
            else:
                error = True
                return HttpResponse(json.dumps({'errors': error}),content_type='application/json')

        return render(request, 'users/login.html')

def home(request):
    link = Link.objects.all()
    notification = Notification.objects.all()
    return render(request, 'users/home.html', {'link':link, 'notif': notification})

def newUser(request):
    return render(request, 'users/register.html')

@login_required
def userLogout(request):
    del request.session['username']
    del request.session['password'] 
    logout(request)
    return HttpResponseRedirect("/judge/login")

@login_required
def problem(request, contestId, problemId):
    problem = Problem.objects.filter(contest_id=contestId, id=problemId)
    comment = Comments.objects.filter(problem_id=problemId, contest_id=contestId)
    language = Language.objects.all()
    return render(request, 'users/problem.html', {'problem': problem, 'language':language, 'comment':comment})

@login_required
def index(request):
    currentContest = Contest.objects.filter(startTime__lte=datetime.now(), endTime__gt=datetime.now()) 
    futureContest = Contest.objects.filter(startTime__gt=datetime.now())
    pastContest = Contest.objects.filter(endTime__lt=datetime.now())
    return render(request, 'users/index.html', {'futureContest': futureContest, 'pastContest': pastContest, 'currentContest': currentContest })

@login_required
def contest(request, contestId):
    problem = Problem.objects.filter(contest_id=contestId)
    return render(request, 'users/contest.html', {'problem': problem})

@login_required
def profile(request):
    hacker = Hacker.objects.filter(username = request.session['username'])
    h = Hacker.objects.get(username=request.session['username'])
    solution = Solution.objects.filter(hacker_id = h.id)
    cont = Contest.objects.all()
    l1 = []
    for c in cont:
        l2 = [False]*c.problem_set.all().size()
        l1.append(l2)
    for c in cont:
        SolSet = c.solution_set.all()
        ProSet = c.problem_set.all()
        for p in ProSet:
            ProSolSet= p.SolSet_set.all()
            for x in ProSolSet:
                if x.status == 4:
                    print "yeah"
    return render(request, 'users/profile.html', {'hacker':hacker, 'sols': l1})  

@login_required
def changeProfilePic(request):
    if request.method == 'POST':
        m = Hacker.objects.get(username=request.session['username'])
        m.profileImage = request.FILES['image']
        m.save()
        return HttpResponseRedirect('/judge/profile')
    return HttpResponseForbidden('allowed only via POST')

@login_required
def removeProfilePic(request):
    if request.method == 'POST':
        m = Hacker.objects.get(username=request.session['username'])
        m.profileImage = ""
        m.save()
        return HttpResponseRedirect('/judge/profile')
    return HttpResponseForbidden('allowed only via POST')

@login_required
def success(request):
    return render(request, 'users/success.html')

@login_required
def submission(request):
    h = Hacker.objects.get(username=request.session['username'])
    solution = Solution.objects.filter(hacker_id = h.id)
    return render(request, 'users/submission.html', {'solution': solution})

@login_required
def changePassword(request):
    print "booohhyeahhh!"
    error = 0
    if request.method == "POST":
        print "viva barca"
        old_password = request.POST['oldPassword']
        new_password = request.POST['newPassword']
        print old_password, new_password
        user = authenticate(username=request.session['username'], password=old_password)
        if user is not None:
            query = Hacker.objects.get(username=request.session['username'])
            query.set_password(new_password)
            query.save()
            error = 1
            t = loader.get_template('users/profile.html')
            c = RequestContext(request, {'error': error})
            return HttpResponse(t.render(c))
        else:
            error = 2
            t = loader.get_template('users/profile.html')
            c = RequestContext(request, {'error': error})
            return HttpResponse(t.render(c))

@login_required
def change(request):
    return render(request, 'users/changepass.html')

@login_required
def comment(request):
    h = Hacker.objects.get(username=request.session['username'])
    c = Contest.objects.get(id = request.POST['cid'])
    p = Problem.objects.get(id = request.POST['pid'])
    comment = Comments(commentText=request.POST['comment'], hacker=h, contest=c, problem=p)
    comment.save()
    url = "/judge/"+str(c.id)+"/problem/"+str(p.id)
    return HttpResponseRedirect(url)


@login_required
def submitSolution(request):
    if request.method == 'POST':
        h = Hacker.objects.get(username=request.session['username'])
        c = Contest.objects.get(id = request.POST['cid'])
        p = Problem.objects.get(id = request.POST['pid'])
        l = Language.objects.get(id = request.POST['lid'])
        payload = {'fmt':'json', 'username':request.session['username'], 'password':request.session['password']}
        auth = requests.get("http://localhost:8000/v1/getAuthID",payload)
        answer = auth.json()
        sol = Solution(hacker=h, contest=c, problem =p , points=0, language=l, attempts=0, time=0.0, status=0)
        sol.save()
        url = 'http://localhost:8000/v1/file?authid={0}&op=upload&filepath={1}'.format(answer['authid'],str(sol.id) + "." + str(l.extension))
        r = requests.post(url,request.POST['solutionBox'])
        url = 'http://localhost:8000/v1/file?authid={0}&op=download&filepath={1}'.format(answer['authid'],str(sol.id) + "." + str(l.extension))
        req = requests.get(url)
        answer = req.json()
        sol.solution = answer['msg']
        sol.save()
        inputFile = settings.MEDIA_ROOT + str(p.testInput)
        outputFile = settings.MEDIA_ROOT + str(p.testOutput)
        file1 = open(inputFile, 'r')
        input = file1.read()
        file2 = open(outputFile, 'r')
        output = file2.read()
        sock = Socket()

        file_name = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
        text_file = open(file_name + ".cpp", "w")
        text_file.write(request.POST['solutionBox'])
        text_file.close()


        filepath = os.getcwd() + '/' + file_name + '.cpp'
        arg = "g++ " + filepath + ' -o ' + os.getcwd() + '/' + file_name

        print "\n \n ARG :- ", arg
        os.system(arg);



        filepath = os.getcwd() + '/' + file_name

        # print filepath

        print "File Name " + str(sol.id) + "." + str(l.extension)
        sock.connect("127.0.0.1", 6029)
        temp = json.dumps({'id': sol.id, 
             'filepath': filepath,
             # 'filepath': str(sol.id) + "." + str(l.extension),
             # 'code': request.POST['solutionBox'],
             # 'language': l.language,
             'input': input,
             'output': output,
             # 'matchLines': 0,
             # 'partial': 0,
             # 'points':p.points,
             'time': p.timeLimit})
        sock.send(temp)
        return HttpResponseRedirect('/judge/success')
    return HttpResponseForbidden('allowed only via POST')


def register(request): 
    errors = False
    if request.method == 'POST' and request.is_ajax():
        username = request.POST['user_name']
        password = request.POST['pass_word']
        email = request.POST['email']
        roll = request.POST['roll']

        query = Hacker.objects.filter(username=username)
        if query:
            errors = True
        else:
            user = Hacker.objects.create_user(username, email, roll, password)
            user.save()
            payload = {'username':username,'password':password,'email':email}
            requests.get("http://localhost:8000/v1/userRegister",params=payload)
            user = authenticate(username=username, password=password)
            login(request, user)
            
            request.session['username']  = username
            request.session['password']  = password
            print request.session['username']
            
        return HttpResponse(json.dumps({'errors': errors}),content_type='application/json')
    else:
        raise Http404

def trial(request):
    return HttpResponse(11111111)
