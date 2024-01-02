from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm): 
    class Meta:
        model = Profile
        fields = ['avatar', 'dob', 'gender', 'address', 'phone']

     # Add first_name and last_name fields explicitly
    first_name = forms.CharField(max_length=30, label='First Name', required=False)
    last_name = forms.CharField(max_length=30, label='Last Name', required=False)
    email = forms.CharField(max_length=30, label='Email', required=False, widget=forms.TextInput(attrs={'type': 'email'}))

    # Customizing specific fields
    avatar = forms.ImageField(label='New Avatar', required=False)
    dob = forms.DateField(label='Date of Birth', widget=forms.TextInput(attrs={'type': 'date'}), required=False)
    address = forms.CharField(max_length=255, label='Address', required=False)
    phone = forms.CharField(max_length=10, label='Phone', required=False)
    gender = forms.ChoiceField(
    label='Gender',
    choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
    required=False,
    widget=forms.Select(attrs={'class': 'form-select mb-0', 'aria-label': 'Gender select example'})
)
    def save(self, commit=True):
        # Save the Profile instance
        profile = super().save(commit=False)

        # Set first_name and last_name on the User instance (if it exists)
        user = profile.user
        if user:
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            if commit:
                user.save()

        if commit:
            profile.save()

        return profile
