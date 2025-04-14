from django import forms

class FeedbackForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, label="Ваше ім'я")
    email = forms.EmailField(required=True, label="Ваша електронна пошта")
    message = forms.CharField(widget=forms.Textarea, required=True, label="Ваше повідомлення")
    file = forms.FileField(required=False, label="Прикріпити файл")
    recaptcha = forms.CharField(widget=forms.HiddenInput(), required=True)
