from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
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

    # def clean_email(self):
    #     email = self.cleaned_data["email"]
    #     try:
    #         validate_email(email)
    #     except ValidationError:
    #         raise ValidationError("正しいメールアドレスを指定して下さい。")

    #     try:
    #         CustomUser.objects.filter(email=email).order_by("-id").first()
    #     except CustomUser.DoesNotExist:
    #         return email
    #     else:
    #         raise ValidationError("このメールアドレスは既に使用されています。別のメールアドレスを指定してください")

class CustomUserEditForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30,required=True)
    last_name = forms.CharField(max_length=30,required=True)
    # パスワード入力：非表示対応
    password = forms.CharField(widget=forms.PasswordInput(),label="パスワード")

    def __init__(self, user, *args, **kwargs):
        self.login_user = user
        super().__init__(*args, **kwargs)

    class Meta():
        # ユーザー認証
        model = CustomUser
        # フィールド指定
        fields = ('last_name','first_name','number','username','email','password',)
        # フィールド名指定
        labels = {'last_name':"名字",'first_name':"名前", 'number':"学生番号",'username':"ユーザー名",'email':"メールアドレス"}

    # def clean_email(self):
    #     email = self.cleaned_data["email"]
    #     try:
    #         validate_email(email)
    #     except ValidationError:
    #         raise ValidationError("正しいメールアドレスを指定して下さい。")

    #     try:
    #         CustomUser.objects.filter(email=email).order_by("-id").first()
    #     except CustomUser.DoesNotExist:
    #         return email
    #     else:
    #         if self.login_user.email == email:
    #             return email
    #         raise ValidationError("このメールアドレスは既に使用されています。別のメールアドレスを指定してください")
