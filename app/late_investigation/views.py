
import datetime
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth import authenticate
from .forms import CustomUserForm, CustomUserEditForm, RouteForm, RouteInlineFormSet # ユーザーアカウントフォーム
from .models import CustomUser, Delay, Route, UserDelay
from .routeinfo import getinfo

dt_now_jst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
now = {"year": dt_now_jst.year,"month": dt_now_jst.month,"day": dt_now_jst.day,}
info = getinfo()

class Home(TemplateView):

    def __init__(self):
        self.params = {
            "user_route_ids": [route.id for route in Route.objects.all()],
            "delays": Delay.objects.all(),
            "delay_ids": [],
            "UserDelayCreate": False,
        }

    # Get処理
    def get(self,request):
        if request.user.id is None:
            return redirect('/login')
        self.params["user_route_ids"] = [route.id for route in request.user.routes.all()]
        self.params["delays"] = Delay.objects.all()
        self.params["delay_ids"] = [userdelay.delay.id for userdelay in UserDelay.objects.filter(user=request.user)]
        self.params["UserDelayCreate"] = False
        return render(request,"home.html", context=self.params)

    # Post処理
    def post(self,request):
        user = request.user
        checked_delay_ids = [int(delay_id) for delay_id in request.POST.getlist("checked_delay")]
        delay_ids = [userdelay.delay.id for userdelay in UserDelay.objects.filter(user=user)]
        unchecked_delay_ids = list(set(delay_ids) - set(checked_delay_ids))

        for delay_id in unchecked_delay_ids:
            delay = Delay.objects.get(id=delay_id)
            UserDelay.objects.filter(user=user,delay=delay)[0].delete()

        add_delay_ids = [int(delay_id) for delay_id in request.POST.getlist("delay")]
        for delay_id in add_delay_ids:
            delay = Delay.objects.filter(id=delay_id)[0]
            if delay.route in user.routes.all():
                UserDelay(user=user,delay=delay).save()

        self.params["user_route_ids"] = [route.id for route in request.user.routes.all()]
        self.params["delays"] = Delay.objects.all()
        self.params["delay_ids"] = [userdelay.delay.id for userdelay in UserDelay.objects.filter(user=user)]
        self.params["UserDelayCreate"] = True

        return render(request,"home.html", context=self.params)

class UserRegister(TemplateView):

    def __init__(self):
        self.params = {
            "AccountCreate": False,
            "custom_user_form": CustomUserForm(),
        }

    # Get処理
    def get(self,request):
        self.params["custom_user_form"] = CustomUserForm()
        self.params["AccountCreate"] = False
        return render(request,"registration/register.html", context=self.params)

    # Post処理
    def post(self,request):
        self.params["custom_user_form"] = CustomUserForm(data=request.POST)

        # フォーム入力の有効検証
        if self.params["custom_user_form"].is_valid():
            # アカウント情報をDB保存
            custom_user = self.params["custom_user_form"].save()
            # パスワードをハッシュ化
            custom_user.set_password(custom_user.password)
            # ハッシュ化パスワード更新
            custom_user.save()

            # アカウント作成情報更新
            self.params["AccountCreate"] = True

        else:
            # フォームが有効でない場合
            print(self.params["custom_user_form"].errors)

        return render(request, "registration/register.html", context=self.params)

class UserEdit(TemplateView):

    def __init__(self):
        self.params = {
            "AccountChange": False,
            "custom_user_edit_form": CustomUserEditForm(user=None),
            "route_formset": RouteInlineFormSet(),
        }

    # Get処理
    def get(self,request):
        user = request.user
        self.params["custom_user_edit_form"] = CustomUserEditForm(user=user, instance=user)
        self.params["route_formset"] = RouteInlineFormSet(instance=user)
        self.params["AccountChange"] = False
        return render(request,"users/edit.html", context=self.params)

    # Post処理
    def post(self,request):
        user = request.user
        self.params["custom_user_edit_form"] = CustomUserEditForm(user=user, instance=user, data=request.POST)
        self.params["route_formset"] = RouteInlineFormSet(instance=user, data=request.POST)

        # フォーム入力の有効検証
        if self.params["custom_user_edit_form"].is_valid():
            # アカウント情報をDB保存
            custom_user = self.params["custom_user_edit_form"].save(commit=False)
            if self.params["route_formset"].is_valid():
                custom_user.save()
                self.params["route_formset"].save()

                new_password = self.params["custom_user_edit_form"].cleaned_data.get("new_password")
                if new_password != "":
                    # パスワードをハッシュ化
                    custom_user.set_password(new_password)
                    # ハッシュ化パスワード更新
                    custom_user.save()

            # アカウント編集情報更新
            self.params["AccountChange"] = True

        else:
            # フォームが有効でない場合
            print(self.params["custom_user_edit_form"].errors)

        return render(request, "users/edit.html", context=self.params)

    def get_object(self):
        return self.request.user

class Routelist(TemplateView):

    def __init__(self):
        self.params = {
            "route_form": RouteForm(),
            "routes": Route.objects.all(),
        }

    # Get処理
    def get(self,request):
        user = request.user
        self.params["route_form"] = RouteForm()
        self.params["routes"] = Route.objects.all()
        return render(request,"routes/list.html", context=self.params)

    # Post処理
    def post(self,request):
        self.params["route_form"] = RouteForm(data=request.POST)

        # フォーム入力の有効検証
        if self.params["route_form"].is_valid():
            # 路線情報をDB保存
            self.params["route_form"].save()

        else:
            # フォームが有効でない場合
            print(self.params["route_form"].errors)

        return render(request, "routes/list.html", context=self.params)

class DelayRegister(TemplateView):

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
        # if request.user.is_teacher is False:
        #     return render(request, "home.html")

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
        self.params["today_delay_routes"] = [delay.route for delay in Delay.objects.filter(**now)]

        checked_delay_route_ids = [int(route_id) for route_id in request.POST.getlist("checked_delay")]
        delay_route_ids = [route.id for route in self.params["today_delay_routes"]]
        unchecked_delay_route_ids = list(set(delay_route_ids) - set(checked_delay_route_ids))
        for route_id in unchecked_delay_route_ids:
            Delay.objects.filter(route_id=route_id,**now)[0].delete()

        add_delay_route_ids = [int(route_id) for route_id in request.POST.getlist("delay")]
        for route_id in add_delay_route_ids:
            Delay(route_id=route_id).save()

        self.params["DelayCreate"] = True

        return render(request,"delay/register.html", context=self.params)

    # Update処理
    def update(self,request):
        # if request.user.is_teacher is False:
        #     return render(request, "home.html")

        self.updateinfo()
        return render(request,"delay/register.html", context=self.params)

class UserDelayRegister(TemplateView):

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
        checked_delay_ids = [int(delay_id) for delay_id in request.POST.getlist("checked_delay")]
        delay_ids = [userdelay.delay.id for userdelay in UserDelay.objects.filter(user=user)]
        unchecked_delay_ids = list(set(delay_ids) - set(checked_delay_ids))

        for delay_id in unchecked_delay_ids:
            delay = Delay.objects.get(id=delay_id)
            UserDelay.objects.filter(user=user,delay=delay)[0].delete()

        add_delay_ids = [int(delay_id) for delay_id in request.POST.getlist("delay")]
        for delay_id in add_delay_ids:
            delay = Delay.objects.filter(id=delay_id)[0]
            if delay.route in user.routes.all():
                UserDelay(user=user,delay=delay).save()

        self.params["user_route_ids"] = [route.id for route in request.user.routes.all()]
        self.params["delays"] = Delay.objects.all()
        self.params["delay_ids"] = [userdelay.delay.id for userdelay in UserDelay.objects.filter(user=user)]
        self.params["UserDelayCreate"] = True

        return render(request,"userdelay/register.html", context=self.params)

class UserDelayList(TemplateView):

    def __init__(self):
        self.params = {
            "userdelays": UserDelay.objects.all(),
            "finished_userdelay_ids": [],
            "FinishUpdate": False
        }

    # Get処理
    def get(self,request):
        self.params["userdelays"] = UserDelay.objects.all()
        self.params["finished_userdelay_ids"] = [userdelay.id for userdelay in UserDelay.objects.filter(is_finished=True)]
        self.params["FinishUpdate"] = False
        return render(request,"userdelay/list.html", context=self.params)

    # Post処理
    def post(self,request):
        user = request.user
        checked_userdelay_ids = [int(delay_id) for delay_id in request.POST.getlist("checked_finish")]
        finished_userdelay_ids = [userdelay.id for userdelay in UserDelay.objects.filter(is_finished=True)]
        unchecked_userdelay_ids = list(set(finished_userdelay_ids) - set(checked_userdelay_ids))

        for userdelay_id in unchecked_userdelay_ids:
            userdelay = UserDelay.objects.get(id=userdelay_id)
            userdelay.is_finished = False
            userdelay.save()

        add_userdelay_ids = [int(userdelay_id) for userdelay_id in request.POST.getlist("finish")]
        for userdelay_id in add_userdelay_ids:
            userdelay = UserDelay.objects.get(id=userdelay_id)
            userdelay.is_finished = True
            userdelay.save()

        self.params["user_routes"] = user.routes
        self.params["finished_userdelay_ids"] = [userdelay.id for userdelay in UserDelay.objects.filter(is_finished=True)]
        self.params["FinishUpdate"] = True

        return render(request,"userdelay/list.html", context=self.params)

class UserDelayHistory(TemplateView):

    def __init__(self):
        self.params = {
            "userdelays": UserDelay.objects.all(),
        }

    # Get処理
    def get(self,request):
        self.params["userdelays"] = UserDelay.objects.filter(user=request.user)
        return render(request,"userdelay/history.html", context=self.params)
