from django.shortcuts import render
from django.views.generic import TemplateView # テンプレートタグ
from .forms import CustomUserForm # ユーザーアカウントフォーム
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

def home(request):
    return render(request, 'home.html')

class AccountRegistration(TemplateView):

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
            print(self.params["account_form"].errors)

        return render(request, "registration/register.html", context=self.params)
