from django import forms
from .models import CustomUser

# フォームクラス作成
class CustomUserForm(forms.ModelForm):
    # パスワード入力：非表示対応
    password = forms.CharField(widget=forms.PasswordInput(),label="パスワード")

    class Meta():
        # ユーザー認証
        model = CustomUser
        # フィールド指定
        fields = ('last_name','first_name','username','email','password',)
        # フィールド名指定
        labels = {'last_name':"名字",'first_name':"名前",'username':"ユーザー名",'email':"メールアドレス"}
