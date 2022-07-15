from django.shortcuts import render
from django.views.generic import TemplateView # テンプレートタグ
from .forms import CustomUserForm, CustomUserEditForm # ユーザーアカウントフォーム
from .models import CustomUser
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

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
        }

    # Get処理
    def get(self,request):
        user = request.user
        self.params["custom_user_edit_form"] = CustomUserEditForm(user=user, instance=user)
        self.params["AccountChange"] = False
        return render(request,"users/edit.html", context=self.params)

    # Post処理
    def post(self,request):
        user = request.user
        self.params["custom_user_edit_form"] = CustomUserEditForm(user=user, instance=user, data=request.POST)

        # フォーム入力の有効検証
        if self.params["custom_user_edit_form"].is_valid():
            # アカウント情報をDB保存
            custom_user = self.params["custom_user_edit_form"].save()
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
