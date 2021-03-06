
import datetime
import numbers
from unicodedata import name
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomUserForm, CustomUserEditForm, RouteForm, RouteInlineFormSet, RouteInlineFormSetNotDelete # ユーザーアカウントフォーム
from .models import CustomUser, Delay, Route, UserDelay
from .routeinfo import getinfo

dt_now_jst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
now = {"year": dt_now_jst.year,"month": dt_now_jst.month,"day": dt_now_jst.day,}
info = getinfo()
MAX_GRADE = 7
MAX_COURSE = 4
CLASS_NUMBERS = [i*1000 + j*100 for i in range(1, MAX_GRADE+1) for j in range(1, MAX_COURSE+1)]

class Home(LoginRequiredMixin, TemplateView):

    def __init__(self):
        self.params = {
            "today": str(now.get("year"))+"年"+str(now.get("month"))+"月"+str(now.get("day"))+"日",
            "user_route_ids": [],
            "delays": Delay.objects.all(),
            "is_existed": False,
            "delay_ids": [],
        }

    # Get処理
    def get(self,request):
        if request.user.is_staff:
            return redirect('/delay/register')
        if request.user.is_teacher:
            return redirect('/user/delay')

        self.params["today"] = str(now.get("year"))+"年"+str(now.get("month"))+"月"+str(now.get("day"))+"日"
        self.params["user_route_ids"] = [route.id for route in request.user.routes.all()]
        self.params["delays"] = Delay.objects.filter(**now)
        self.params["is_existed"] = len(self.params["delays"]) != 0
        self.params["delay_ids"] = [userdelay.delay.id for userdelay in UserDelay.objects.filter(user=request.user)]
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
        self.params["delays"] = Delay.objects.filter(**now)
        self.params["delay_ids"] = [userdelay.delay.id for userdelay in UserDelay.objects.filter(user=user)]

        messages.add_message(request, messages.SUCCESS, "登録成功")
        return redirect("/")

class UserRegister(TemplateView):

    def __init__(self):
        self.params = {
            "user_form": CustomUserForm(),
            "route_formset": RouteInlineFormSetNotDelete(),
        }

    # Get処理
    def get(self,request):
        self.params["user_form"] = CustomUserForm()
        self.params["route_formset"] = RouteInlineFormSetNotDelete()
        return render(request,"registration/register.html", context=self.params)

    # Post処理
    def post(self,request):
        self.params["user_form"] = CustomUserForm(data=request.POST)
        self.params["route_formset"] = RouteInlineFormSetNotDelete(data=request.POST)

        number = int(request.POST["number"])
        if number // 100 * 100 not in CLASS_NUMBERS:
            self.set_form_error(request=request)
            messages.error(request, "正しい学生番号を入力して下さい")
            return render(request, "registration/register.html", context=self.params)

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

            messages.add_message(request, messages.SUCCESS, "ユーザ登録成功")
            return redirect("/login")

        self.set_form_error(request=request)
        return render(request, "registration/register.html", context=self.params)

    def set_form_error(self, request):
        values = self.params["user_form"].errors.get_json_data().values()
        for value in values:
            for v in value:
                messages.error(request, v["message"])

        for route_form in self.params["route_formset"]:
            values = route_form.errors.get_json_data().values()
            for value in values:
                for v in value:
                    messages.error(request, v["message"])

class UserEdit(LoginRequiredMixin, TemplateView):

    def __init__(self):
        self.params = {
            "user_edit_form": CustomUserEditForm(),
            "route_formset": RouteInlineFormSet(),
        }

    # Get処理
    def get(self,request):
        user = request.user
        if user.is_teacher and user.number not in CLASS_NUMBERS:
            messages.error(request, "先生は学生番号に担任のクラス番号を入力して下さい")

        self.params["user_edit_form"] = CustomUserEditForm(instance=user)
        self.params["route_formset"] = RouteInlineFormSet(instance=user)
        return render(request,"user/edit.html", context=self.params)

    # Post処理
    def post(self,request):
        user = request.user
        self.params["user_edit_form"] = CustomUserEditForm(instance=user, data=request.POST)
        self.params["route_formset"] = RouteInlineFormSet(instance=user, data=request.POST)

        number = int(request.POST["number"])
        if user.is_teacher:
            if number in CLASS_NUMBERS:
                self.set_form_error(request=request)
                messages.error(request, "先生は学生番号に担任のクラス番号を入力して下さい")
                return render(request, "user/edit.html", context=self.params)
        elif not user.is_staff and (number in CLASS_NUMBERS or number // 100 * 100 not in CLASS_NUMBERS):
            self.set_form_error(request=request)
            messages.error(request, "正しい学生番号を入力して下さい")
            return render(request, "user/edit.html", context=self.params)

        # フォーム入力の有効検証
        if self.params["user_edit_form"].is_valid():
            # アカウント情報をDB保存
            user = self.params["user_edit_form"].save(commit=False)
            if self.params["route_formset"].is_valid():
                user.save()
                self.params["route_formset"].save()
                messages.add_message(request, messages.SUCCESS, "ユーザ編集成功")

                new_password = self.params["user_edit_form"].cleaned_data.get("new_password")
                if new_password != "":
                    # パスワードをハッシュ化
                    user.set_password(new_password)
                    # ハッシュ化パスワード更新
                    user.save()
                    messages.add_message(request, messages.INFO, "パスワードが変更されたので、再度ログインしてください")
                    redirect("/login")
                return redirect("/")

        self.set_form_error(request=request)
        return render(request, "user/edit.html", context=self.params)

    def set_form_error(self, request):
        values = self.params["user_edit_form"].errors.get_json_data().values()
        for value in values:
            for v in value:
                messages.error(request, v["message"])

        for route_form in self.params["route_formset"]:
            values = route_form.errors.get_json_data().values()
            for value in values:
                for v in value:
                    messages.error(request, v["message"])

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
        if request.user.is_staff is False:
            return redirect('/')

        self.params["routes"] = Route.objects.all()
        return render(request,"route/list.html", context=self.params)

    # Post処理
    def post(self,request):
        if request.user.is_staff is False:
            return redirect('/')

        name = request.POST.get("name")
        # フォーム入力の有効検証
        if name != "":
            # 路線情報をDB保存
            Route(name=name).save()
            messages.add_message(request, messages.SUCCESS, "登録成功")

        checked_route_ids = [int(route_id) for route_id in request.POST.getlist("delete")]
        for route_id in checked_route_ids:
            Route.objects.get(id=route_id).delete()

        self.params["routes"] = Route.objects.all()
        return render(request, "route/list.html", context=self.params)

class DelayRegister(LoginRequiredMixin, TemplateView):

    def __init__(self):
        self.params = {
            "infos" : [],
            "today": str(now.get("year"))+"年"+str(now.get("month"))+"月"+str(now.get("day"))+"日",
            "today_delay_routes": [delay.route for delay in Delay.objects.filter(**now)],
        }

    def updateinfos(self):
        dt_now_jst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        now = {"year": dt_now_jst.year,"month": dt_now_jst.month,"day": dt_now_jst.day,}
        info = getinfo()

    # Get処理
    def get(self,request):
        if request.user.is_staff is False:
            return redirect('/')

        routes = Route.objects.all()
        times = [info.get(route.name) if route.name in info else "不明" for route in routes]
        infos = []
        for i in range(len(routes)):
            infos.append({'route':routes[i], 'time':times[i]})
        self.params["infos"] = infos
        self.params["today"] = str(now.get("year"))+"年"+str(now.get("month"))+"月"+str(now.get("day"))+"日"
        self.params["today_delay_routes"] = [delay.route for delay in Delay.objects.filter(**now)]
        return render(request,"delay/register.html", context=self.params)

    # Post処理
    def post(self,request):
        if request.user.is_staff is False:
            return redirect('/')

        if "update" in request.POST:
            self.updateinfos()
            messages.add_message(request, messages.INFO, "情報の更新が完了しました")
            return redirect("/delay/register")

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

        messages.add_message(request, messages.SUCCESS, "登録成功")
        return redirect("/delay/register")

class UserDelayRegister(LoginRequiredMixin, TemplateView):

    def __init__(self):
        self.params = {
            "user_route_ids": [route.id for route in Route.objects.all()],
            "delays": Delay.objects.all(),
            "delay_ids": [],
        }

    # Get処理
    def get(self,request):
        self.params["user_route_ids"] = [route.id for route in request.user.routes.all()]
        self.params["delays"] = Delay.objects.all()
        self.params["delay_ids"] = [userdelay.delay.id for userdelay in UserDelay.objects.filter(user=request.user)]
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

        messages.add_message(request, messages.SUCCESS, "登録成功")
        return render(request,"userdelay/register.html", context=self.params)

class UserDelayList(LoginRequiredMixin, TemplateView):

    def __init__(self):
        self.params = {
            "userdelays": UserDelay.objects.all(),
        }

    # Get処理
    def get(self,request):
        user = request.user
        if not user.is_staff and not user.is_teacher:
            return redirect('/')

        self.params["userdelays"] = UserDelay.objects.all()
        if "class_number" in request.GET:
            class_number = request.GET.get("class_number")
            if class_number != "" and int(class_number) in CLASS_NUMBERS:
                class_number = int(class_number)
                self.params["class_number"] = class_number
                self.params["userdelays"] = [userdelay for userdelay in UserDelay.objects.all() if userdelay.user.number // 100 == class_number // 100]
        elif user.is_teacher:
            if user.number in CLASS_NUMBERS:
                return redirect("/user/delay/?class_number="+str(user.number))
            elif not user.is_staff:
                messages.error(request, "正しい学生番号を入力して下さい")
                return redirect("/user/edit", context=self.params)

        self.params["class_numbers"] = CLASS_NUMBERS
        return render(request,"userdelay/list.html", context=self.params)

    # Post処理
    def post(self,request):
        user = request.user
        if user.is_staff is False and user.is_teacher is False:
            return redirect('/')

        checked_checked_userdelay_ids = [int(userdelay_id) for userdelay_id in request.POST.getlist("check")]
        checked_userdelay_ids = [userdelay.id for userdelay in UserDelay.objects.filter(is_checked=True)]
        add_checked_userdelay_ids = list(set(checked_checked_userdelay_ids) - set(checked_userdelay_ids))
        delete_checked_userdelay_ids = list(set(checked_userdelay_ids) - set(checked_checked_userdelay_ids))

        checked_finished_userdelay_ids = [int(userdelay_id) for userdelay_id in request.POST.getlist("finish")]
        finished_userdelay_ids = [userdelay.id for userdelay in UserDelay.objects.filter(is_finished=True)]
        add_finished_userdelay_ids = list(set(checked_finished_userdelay_ids) - set(finished_userdelay_ids))
        delete_finished_userdelay_ids = list(set(finished_userdelay_ids) - set(checked_finished_userdelay_ids))

        checked_is_not_changed = len(add_checked_userdelay_ids) == 0 and len(delete_checked_userdelay_ids) == 0
        finished_is_not_changed = len(add_finished_userdelay_ids) == 0 and len(delete_finished_userdelay_ids) == 0
        if checked_is_not_changed and finished_is_not_changed:
            return redirect("/user/delay/" + "?class_number="+request.GET["class_number"] if "class_number" in request.GET else "")

        for userdelay_id in add_checked_userdelay_ids:
            userdelay = UserDelay.objects.get(id=userdelay_id)
            userdelay.is_checked = True
            userdelay.save()

        for userdelay_id in delete_checked_userdelay_ids:
            userdelay = UserDelay.objects.get(id=userdelay_id)
            userdelay.is_checked = False
            userdelay.save()

        for userdelay_id in add_finished_userdelay_ids:
            userdelay = UserDelay.objects.get(id=userdelay_id)
            userdelay.is_finished = True
            userdelay.save()

        for userdelay_id in delete_finished_userdelay_ids:
            userdelay = UserDelay.objects.get(id=userdelay_id)
            userdelay.is_finished = False
            userdelay.save()

        messages.add_message(request, messages.SUCCESS, "登録成功")
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
        }

    # Get処理
    def get(self,request):
        if request.user.is_staff is False:
            return redirect('/')

        self.params["users"] = CustomUser.objects.all()
        self.params["teacher_ids"] = [user.id for user in CustomUser.objects.filter(is_teacher=True)]
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

        messages.add_message(request, messages.SUCCESS, "登録成功")
        return render(request,"user/list.html", context=self.params)
