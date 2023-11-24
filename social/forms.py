from django import forms
from .models import User, Post, Comment
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(forms.Form):
    username = forms.CharField(max_length=200, required=True, label="نام کاربری یا تلفن", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=200, required=True, label="رمز عبور", widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UserRegisterForm(forms.ModelForm):
    password1 = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='پسورد')
    password2 = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='تکرار پسورد')

    class Meta:
        model = User
        fields = ['username', 'phone', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': 'نام کاربری',
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'phone': 'شماره تماس',
        }

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] != cd['password2']:
            raise forms.ValidationError('پسورد ها مطابقت ندارند')
        return cd['password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("این نام کاربری وجود دارد")
        return username

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("این شماره تلفن وجود دارد")
        return phone


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'bio', 'photo', 'job']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control'}),
            'bio': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'job': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': 'نام کاربری',
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'email': 'ایمیل',
            'date_of_birth': 'تاریخ تولد',
            'phone': 'شماره تماس',
            'bio': 'بایو',
            'job': 'شغل',
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.exclude(id=self.instance.id).filter(username=username).exists():
            raise forms.ValidationError("نام کاربری وجود دارد")
        return username

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if User.objects.exclude(id=self.instance.id).filter(phone=phone).exists():
            raise forms.ValidationError("شماره تلفن وجود دارد")
        return phone


class TicketForm(forms.Form):
    SUBJECT_CHOICES = (
        ('پیشنهاد', 'پیشنهاد'),
        ('انتقاد', 'انتقاد'),
        ('گزارش', 'گزارش'),
    )
    name = forms.CharField(max_length=100, required=True, label='نام', widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(max_length=100, required=True, label='ایمیل', widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=11, required=True, label='شماره تماس', widget=forms.TextInput(attrs={'class': 'form-control'}))
    message = forms.CharField(max_length=500, required=True, label='پیام', widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}))
    subject = forms.ChoiceField(label='موضوع', choices=SUBJECT_CHOICES)

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            if not phone.isnumeric():
                raise forms.ValidationError("شماره تلفن عددی نیست")
            else:
                return phone


class CreatePostForm(forms.ModelForm):
    image1 = forms.ImageField(label="تصویر اول", widget=forms.FileInput(attrs={'class': 'form-control'}))
    image2 = forms.ImageField(label="تصویر دوم", widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Post
        fields = ['description', 'tags']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
        }
        labels = {
            'tags': 'تگ ها',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.TextInput(attrs={'placeholder': 'کامنت بزارید...', 'class': 'form-control input-sm'}),
        }


class SearchForm(forms.Form):
    query = forms.CharField()
