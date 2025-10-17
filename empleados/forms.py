from django import forms
from accounts.models import CustomUser

class EmpleadoForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'role']
        widgets = {
            'role': forms.HiddenInput(),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'empleado'
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user