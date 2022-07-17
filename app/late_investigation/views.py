from django.shortcuts import render
from django.views.generic import TemplateView # テンプレートタグ
from .forms import CustomUserForm, CustomUserEditForm, RouteForm, RouteInlineFormSet # ユーザーアカウントフォーム
from .models import CustomUser, Delay, Route, UserDelay
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
import datetime

dt_now_jst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
now = {"year": dt_now_jst.year,"month": dt_now_jst.month,"day": dt_now_jst.day,}

def home(request):
    return render(request, 'home.html')

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
            "routes": Route.objects.all(),
            "today_delay_routes": [delay.route for delay in Delay.objects.filter(**now)],
            "DelayCreate": False,
        }

    # Get処理
    def get(self,request):
        # if request.user.is_teacher is False:
        #     return render(request, "home.html")

        self.params["routes"] = Route.objects.all()
        self.params["today_delay_routes"] = [delay.route for delay in Delay.objects.filter(**now)]
        self.params["DelayCreate"] = False
        return render(request,"delay/register.html", context=self.params)

    # Post処理
    def post(self,request):
        self.params["routes"] = Route.objects.all()
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

class UserDelayRegister(TemplateView):

    def __init__(self):
        self.params = {
            "user_routes": Route.objects.all(),
            "delays": Delay.objects.all(),
            "delay_ids": [],
            "DelayCreate": False,
        }

    # Get処理
    def get(self,request):
        self.params["user_routes"] = request.user.routes
        self.params["delays"] = Delay.objects.all()
        self.params["delay_ids"] = [user_delay.delay.id for user_delay in UserDelay.objects.filter(user=request.user)]
        self.params["DelayCreate"] = False
        return render(request,"userdelay/register.html", context=self.params)

    # Post処理
    def post(self,request):
        user = request.user
        checked_delay_ids = [int(delay_id) for delay_id in request.POST.getlist("checked_delay")]
        unchecked_delay_ids = list(set(self.params["delay_ids"]) - set(checked_delay_ids))

        for delay_id in unchecked_delay_ids:
            delay = Delay.objects.get(id=delay_id)
            UserDelay.objects.filter(user=user,delay=delay)[0].delete()

        add_delay_ids = [int(delay_id) for delay_id in request.POST.getlist("delay")]
        for delay_id in add_delay_ids:
            delay = Delay.objects.filter(id=delay_id)[0]
            UserDelay(user=user,delay=delay).save()

        self.params["user_routes"] = user.routes
        self.params["delays"] = Delay.objects.all()
        self.params["delay_ids"] = [user_delay.delay.id for user_delay in UserDelay.objects.filter(user=user)]
        self.params["DelayCreate"] = True

        return render(request,"userdelay/register.html", context=self.params)

class UserDelayList(TemplateView):

    def __init__(self):
        self.params = {
            "userdelays": UserDelay.objects.all(),
        }

    # Get処理
    def get(self,request):
        self.params["userdelays"] = UserDelay.objects.all()
        return render(request,"userdelay/list.html", context=self.params)
