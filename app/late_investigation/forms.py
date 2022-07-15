from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import CustomUser, Route

class RouteRegisterForm(forms.ModelForm):

    class Meta:
        model = CustomUser.route.through
        fields = '__all__'
        labels = {'route':"路線名"}

# インラインフォーム作成
RouteInlineFormSet = forms.inlineformset_factory(
    CustomUser, CustomUser.route.through, form=RouteRegisterForm, can_delete=False, extra=3
)

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

class CustomUserEditForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30,required=True)
    last_name = forms.CharField(max_length=30,required=True)
    # パスワード入力：非表示対応
    new_password = forms.CharField(widget=forms.PasswordInput(),label="新しいパスワード",required=False)

    def __init__(self, user, *args, **kwargs):
        self.login_user = user
        super().__init__(*args, **kwargs)

    class Meta():
        # ユーザー認証
        model = CustomUser
        # フィールド指定
        fields = ('last_name','first_name','number','username','email','new_password',)
        # フィールド名指定
        labels = {'last_name':"名字",'first_name':"名前", 'number':"学生番号",'username':"ユーザー名",'email':"メールアドレス"}

class RouteForm(forms.ModelForm):
    class Meta():
        # ユーザー認証
        model = Route
        # フィールド指定
        fields = ('name',)
        # フィールド名指定
        labels = {'name':"路線名",}
