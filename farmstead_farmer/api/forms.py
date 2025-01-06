from django import forms
from django.utils.timezone import now
from .models import CustomUser

class ProfileUpdateForm(forms.ModelForm):
    current_password = forms.CharField(
        widget=forms.PasswordInput, required=False, label="Теперішній пароль"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput, required=False, label="Новий пароль"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput, required=False, label="Підтвердження нового паролю"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'bio', 'avatar']

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get("current_password")
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")
        user = self.instance

        # Password validation
        if new_password or confirm_password:
            if not current_password:
                raise forms.ValidationError("Введіть теперішній пароль для зміни паролю.")
            if not user.check_password(current_password):
                raise forms.ValidationError("Теперішній пароль неправильний.")
            if new_password != confirm_password:
                raise forms.ValidationError("Новий пароль і підтвердження паролю не співпадають.")

        # Username change validation (once a week)
        if "username" in cleaned_data and user.last_username_update:
            if (now() - user.last_username_update).days < 7:
                raise forms.ValidationError("Зміну імені можна здійснювати лише раз на тиждень.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get("new_password")
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user
