
import datetime
from unicodedata import name
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomUserForm, CustomUserEditForm, RouteForm, RouteInlineFormSet, RouteInlineFormSetNotDelete # ユーザーアカウントフォーム
from .models import CustomUser, Delay, Route, UserDelay
from .routeinfo import getinfo

dt_now_jst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
now = {"year": dt_now_jst.year,"month": dt_now_jst.month,"day": dt_now_jst.day,}
info = getinfo()

class Home(LoginRequiredMixin, TemplateView):

    def __init__(self):
        self.params = {
            "user_route_ids": [],
            "delays": Delay.objects.all(),
            "delay_ids": [],
            "UserDelayCreate": False,
        }

    # Get処理
    def get(self,request):
        if request.user.is_staff:
            return redirect('/user')
        if request.user.is_teacher:
            return redirect('/user/delay')

        self.params["user_route_ids"] = [route.id for route in request.user.routes.all()]
        self.params["delays"] = Delay.objects.all()
        self.params["delay_ids"] = [userdelay.delay.id for userdelay in UserDelay.objects.filter(user=request.user)]
        self.params["UserDelayCreate"] = False
        return render(request,"home.html", context=self.params)

    # Post処理
    def post(self,request):
        user = request.user
        delay_ids = [userdelay.delay.id for userdelay in UserDelay.objects.filter(user=user)]
        checked_delay_ids = [int(delay_id) for delay_id in request.POST.getlist("delay")]
        add_delay_ids = list(set(checked_delay_ids) - set(delay_ids))
        delete_delay_ids = list(set(delay_ids) - set(checked_delay_ids))

        if len(add_delay_ids) == 0 and len(delete_delay_ids) == 0:
            return redirect("/")

        for delay_id in add_delay_ids:
            delay = Delay.objects.filter(id=delay_id)[0]
            if delay.route in user.routes.all():
                UserDelay(user=user,delay=delay).save()

        for delay_id in delete_delay_ids:
            delay = Delay.objects.get(id=delay_id)
            UserDelay.objects.filter(user=user,delay=delay)[0].delete()

        self.params["user_route_ids"] = [route.id for route in request.user.routes.all()]
        self.params["delays"] = Delay.objects.all()
        self.params["delay_ids"] = [userdelay.delay.id for userdelay in UserDelay.objects.filter(user=user)]
        self.params["UserDelayCreate"] = True

        return render(request,"home.html", context=self.params)

class UserRegister(TemplateView):

    def __init__(self):
        self.params = {
            "UserCreate": False,
            "user_form": CustomUserForm(),
            "route_formset": RouteInlineFormSetNotDelete(),
        }

    # Get処理
    def get(self,request):
        self.params["user_form"] = CustomUserForm()
        self.params["route_formset"] = RouteInlineFormSetNotDelete()
        self.params["UserCreate"] = False
        return render(request,"registration/register.html", context=self.params)

    # Post処理
    def post(self,request):
        self.params["user_form"] = CustomUserForm(data=request.POST)
        self.params["route_formset"] = RouteInlineFormSetNotDelete(data=request.POST)

        # フォーム入力の有効検証
        if self.params["user_form"].is_valid():
            user = self.params["user_form"].save(commit=False)
            if self.params["route_formset"].is_valid():
                # パスワードをハッシュ化
                user.set_password(user.password)
                # アカウント情報をDB保存
                user.save()
                RouteInlineFormSetNotDelete(instance=user,data=request.POST).save()
            else:
                return render(request, "registration/register.html", context=self.params)

            # アカウント作成情報更新
            self.params["UserCreate"] = True

        return render(request, "registration/register.html", context=self.params)

class UserEdit(LoginRequiredMixin, TemplateView):

    def __init__(self):
        self.params = {
            "UserUpdate": False,
            "PasswordUpdate": False,
            "user_edit_form": CustomUserEditForm(),
            "route_formset": RouteInlineFormSet(),
        }

    # Get処理
    def get(self,request):
        user = request.user
        self.params["user_edit_form"] = CustomUserEditForm(instance=user)
        self.params["route_formset"] = RouteInlineFormSet(instance=user)
        self.params["UserUpdate"] = False
        self.params["PasswordUpdate"] = False
        return render(request,"user/edit.html", context=self.params)

    # Post処理
    def post(self,request):
        user = request.user
        self.params["user_edit_form"] = CustomUserEditForm(instance=user, data=request.POST)
        self.params["route_formset"] = RouteInlineFormSet(instance=user, data=request.POST)

        # フォーム入力の有効検証
        if self.params["user_edit_form"].is_valid():
            # アカウント情報をDB保存
            user = self.params["user_edit_form"].save(commit=False)
            if self.params["route_formset"].is_valid():
                user.save()
                self.params["route_formset"].save()

                new_password = self.params["user_edit_form"].cleaned_data.get("new_password")
                if new_password != "":
                    # パスワードをハッシュ化
                    user.set_password(new_password)
                    # ハッシュ化パスワード更新
                    user.save()
                    self.params["PasswordUpdate"] = True
            else:
                return render(request, "user/edit.html", context=self.params)

            # アカウント編集情報更新
            self.params["UserUpdate"] = True

        return render(request, "user/edit.html", context=self.params)

    def get_object(self):
        return self.request.user

class Routelist(LoginRequiredMixin, TemplateView):

    def __init__(self):
        self.params = {
            "route_form": RouteForm(),
            "routes": Route.objects.all(),
        }

    # Get処理
    def get(self,request):
        if request.user.is_teacher is False:
            return redirect('/')

        self.params["routes"] = Route.objects.all()
        return render(request,"route/list.html", context=self.params)

    # Post処理
    def post(self,request):
        if request.user.is_teacher is False:
            return redirect('/')

        name = request.POST.get("name")
        # フォーム入力の有効検証
        if name != "":
            # 路線情報をDB保存
            Route(name=name).save()

        checked_route_ids = [int(route_id) for route_id in request.POST.getlist("delete")]
        for route_id in checked_route_ids:
            Route.objects.get(id=route_id).delete()

        self.params["routes"] = Route.objects.all()
        return render(request, "route/list.html", context=self.params)

class DelayRegister(LoginRequiredMixin, TemplateView):

    def __init__(self):
        self.params = {
            "infos" : [],
            "today_delay_routes": [delay.route for delay in Delay.objects.filter(**now)],
            "DelayCreate": False,
        }

    def updateinfos(self):
        info = getinfo()
        routes = Route.objects.all()
        times = [info.get(route.name) if route.name in info else "不明" for route in routes]
        infos = []
        for i in range(len(routes)):
            infos.append({'route':routes[i], 'time':times[i]})
        self.params["infos"] = infos

    # Get処理
    def get(self,request):
        if request.user.is_teacher is False:
            return redirect('/')

        routes = Route.objects.all()
        times = [info.get(route.name) if route.name in info else "不明" for route in routes]
        infos = []
        for i in range(len(routes)):
            infos.append({'route':routes[i], 'time':times[i]})
        self.params["infos"] = infos
        self.params["today_delay_routes"] = [delay.route for delay in Delay.objects.filter(**now)]
        self.params["DelayCreate"] = False
        return render(request,"delay/register.html", context=self.params)

    # Post処理
    def post(self,request):
        if request.user.is_teacher is False:
            return redirect('/')

        delay_route_ids = [route.id for route in self.params["today_delay_routes"]]
        checked_delay_route_ids = [int(route_id) for route_id in request.POST.getlist("delay")]
        add_delay_route_ids = list(set(checked_delay_route_ids) - set(delay_route_ids))
        delete_delay_route_ids = list(set(delay_route_ids) - set(checked_delay_route_ids))

        if len(add_delay_route_ids) == 0 and len(delete_delay_route_ids) == 0:
            return redirect("/delay/register")

        for route_id in add_delay_route_ids:
            Delay(route_id=route_id).save()

        for route_id in delete_delay_route_ids:
            Delay.objects.filter(route_id=route_id,**now)[0].delete()

        self.params["today_delay_routes"] = [delay.route for delay in Delay.objects.filter(**now)]
        self.params["DelayCreate"] = True

        return render(request,"delay/register.html", context=self.params)

class UserDelayRegister(LoginRequiredMixin, TemplateView):

    def __init__(self):
        self.params = {
            "user_route_ids": [route.id for route in Route.objects.all()],
            "delays": Delay.objects.all(),
            "delay_ids": [],
            "UserDelayCreate": False,
        }

    # Get処理
    def get(self,request):
        self.params["user_route_ids"] = [route.id for route in request.user.routes.all()]
        self.params["delays"] = Delay.objects.all()
        self.params["delay_ids"] = [userdelay.delay.id for userdelay in UserDelay.objects.filter(user=request.user)]
        self.params["UserDelayCreate"] = False
        return render(request,"userdelay/register.html", context=self.params)

    # Post処理
    def post(self,request):
        user = request.user
        delay_ids = [userdelay.delay.id for userdelay in UserDelay.objects.filter(user=user)]
        checked_delay_ids = [int(delay_id) for delay_id in request.POST.getlist("delay")]
        add_delay_ids = list(set(checked_delay_ids) - set(delay_ids))
        delete_delay_ids = list(set(delay_ids) - set(checked_delay_ids))

        if len(add_delay_ids) == 0 and len(delete_delay_ids) == 0:
            return redirect("/user/delay/register")

        for delay_id in add_delay_ids:
            delay = Delay.objects.filter(id=delay_id)[0]
            if delay.route in user.routes.all():
                UserDelay(user=user,delay=delay).save()

        for delay_id in delete_delay_ids:
            delay = Delay.objects.get(id=delay_id)
            UserDelay.objects.filter(user=user,delay=delay)[0].delete()

        self.params["user_route_ids"] = [route.id for route in request.user.routes.all()]
        self.params["delays"] = Delay.objects.all()
        self.params["delay_ids"] = [userdelay.delay.id for userdelay in UserDelay.objects.filter(user=user)]
        self.params["UserDelayCreate"] = True

        return render(request,"userdelay/register.html", context=self.params)

class UserDelayList(LoginRequiredMixin, TemplateView):

    def __init__(self):
        self.params = {
            "userdelays": UserDelay.objects.all(),
            "finished_userdelay_ids": [],
            "FinishUpdate": False
        }

    # Get処理
    def get(self,request):
        if request.user.is_teacher is False:
            return redirect('/')

        self.params["userdelays"] = UserDelay.objects.all()
        self.params["finished_userdelay_ids"] = [userdelay.id for userdelay in UserDelay.objects.filter(is_finished=True)]
        self.params["FinishUpdate"] = False
        return render(request,"userdelay/list.html", context=self.params)

    # Post処理
    def post(self,request):
        user = request.user
        if user.is_teacher is False:
            return redirect('/')

        checked_userdelay_ids = [int(userdelay_id) for userdelay_id in request.POST.getlist("finish")]
        finished_userdelay_ids = [userdelay.id for userdelay in UserDelay.objects.filter(is_finished=True)]
        add_finished_userdelay_ids = list(set(checked_userdelay_ids) - set(finished_userdelay_ids))
        delete_finished_userdelay_ids = list(set(finished_userdelay_ids) - set(checked_userdelay_ids))

        if len(add_finished_userdelay_ids) == 0 and len(delete_finished_userdelay_ids) == 0:
            return redirect("/user/delay/")

        for userdelay_id in add_finished_userdelay_ids:
            userdelay = UserDelay.objects.get(id=userdelay_id)
            userdelay.is_finished = True
            userdelay.save()

        for userdelay_id in delete_finished_userdelay_ids:
            userdelay = UserDelay.objects.get(id=userdelay_id)
            userdelay.is_finished = False
            userdelay.save()

        self.params["user_routes"] = user.routes
        self.params["finished_userdelay_ids"] = [userdelay.id for userdelay in UserDelay.objects.filter(is_finished=True)]
        self.params["FinishUpdate"] = True

        return render(request,"userdelay/list.html", context=self.params)

class UserDelayHistory(LoginRequiredMixin, TemplateView):

    def __init__(self):
        self.params = {
            "userdelays": UserDelay.objects.all(),
        }

    # Get処理
    def get(self,request):
        self.params["userdelays"] = UserDelay.objects.filter(user=request.user)
        return render(request,"userdelay/history.html", context=self.params)

class UserList(LoginRequiredMixin, TemplateView):

    def __init__(self):
        self.params = {
            "users": CustomUser.objects.all(),
            "teacher_ids": [],
            "FinishUpdate": False
        }

    # Get処理
    def get(self,request):
        if request.user.is_staff is False:
            return redirect('/')

        self.params["users"] = CustomUser.objects.all()
        self.params["teacher_ids"] = [user.id for user in CustomUser.objects.filter(is_teacher=True)]
        self.params["FinishUpdate"] = False
        return render(request,"user/list.html", context=self.params)

    # Post処理
    def post(self,request):
        if request.user.is_staff is False:
            return redirect('/')

        checked_user_ids = [int(user_id) for user_id in request.POST.getlist("teacher")]
        teacher_ids = [userdelay.id for userdelay in CustomUser.objects.filter(is_teacher=True)]
        add_teacher_ids = list(set(checked_user_ids) - set(teacher_ids))
        delete_teacher_ids = list(set(teacher_ids) - set(checked_user_ids))

        if len(add_teacher_ids) == 0 and len(delete_teacher_ids) == 0:
            return redirect("/user")

        for teacher_id in add_teacher_ids:
            user = CustomUser.objects.get(id=teacher_id)
            user.is_teacher = True
            user.save()

        for teacher_id in delete_teacher_ids:
            user = CustomUser.objects.get(id=teacher_id)
            user.is_teacher = False
            user.save()

        self.params["users"] = CustomUser.objects.all()
        self.params["teacher_ids"] = [teacher.id for teacher in CustomUser.objects.filter(is_teacher=True)]
        self.params["FinishUpdate"] = True

        return render(request,"user/list.html", context=self.params)
