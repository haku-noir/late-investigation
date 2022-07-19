from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import CustomUser, Route

class RouteRegisterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['route'].widget.attrs['class'] = 'form-select'

    class Meta:
        model = CustomUser.routes.through
        fields = '__all__'
        labels = {'route':"路線名", 'Delete': "削除"}

# インラインフォーム作成
RouteInlineFormSet = forms.inlineformset_factory(
    CustomUser, CustomUser.routes.through, form=RouteRegisterForm, can_delete=True, extra=3
)

# インラインフォーム作成
RouteInlineFormSetNotDelete = forms.inlineformset_factory(
    CustomUser, CustomUser.routes.through, form=RouteRegisterForm, can_delete=False, extra=3
)

# フォームクラス作成
class CustomUserForm(forms.ModelForm):
    # パスワード入力：非表示対応
    password = forms.CharField(widget=forms.PasswordInput(),label="パスワード")

    class Meta():
        # ユーザ認証
        model = CustomUser
        # フィールド指定
        fields = ('last_name','first_name','number','username','email','password',)
        # フィールド名指定
        labels = {'last_name':"名字",'first_name':"名前",'number':"学生番号",'username':"ユーザ名",'email':"メールアドレス"}

class CustomUserEditForm(forms.ModelForm):
    email = forms.EmailField(label="メールアドレス",required=True)
    first_name = forms.CharField(max_length=30,label="名前",required=True)
    last_name = forms.CharField(max_length=30,label="名字",required=True)
    # パスワード入力：非表示対応
    new_password = forms.CharField(widget=forms.PasswordInput(),label="新しいパスワード",required=False)

    class Meta():
        # ユーザ認証
        model = CustomUser
        # フィールド指定
        fields = ('last_name','first_name','number','username','email','new_password',)
        # フィールド名指定
        labels = {'last_name':"名字",'first_name':"名前",'number':"学生番号",'username':"ユーザ名",'email':"メールアドレス"}

class RouteForm(forms.ModelForm):
    class Meta():
        # ユーザ認証
        model = Route
        # フィールド指定
        fields = ('name',)
        # フィールド名指定
        labels = {'name':"路線名",}
