from django import forms
from .models import Profile
from django.core.validators import RegexValidator



class ProfileForm(forms.ModelForm): 
     # Add first_name and last_name fields explicitly
    first_name = forms.CharField(max_length=30, label='First Name', required=False, widget=forms.TextInput(attrs={'type': 'text', 'class':"form-control", 'placeholder':"Enter your first name"}))
    last_name = forms.CharField(max_length=30, label='Last Name', required=False, widget=forms.TextInput(attrs={'type': 'text', 'class':"form-control", 'placeholder':"Also your last name"}))
    # email = forms.CharField(max_length=30, label='Email', required=False, widget=forms.TextInput(attrs={'type': 'email', 'class':"form-control", 'placeholder':"youremail@gmail.com"}))

    # Customizing specific fields
    dob = forms.DateField(label='Date of Birth', widget=forms.TextInput(attrs={'type': 'date', 'class':"form-control"}), required=False)
    address = forms.CharField(max_length=255, label='address', required=False, widget=forms.TextInput(attrs={'type': 'text', 'class':"form-control", 'placeholder':"Enter your home address"}))
    avatar_input = forms.FileField(label='Avatar', required=False, widget=forms.FileInput(attrs={'type': 'file', 'class':"form-control", 'placeholder':"Choose your avatar"}))
    
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )

    gender = forms.ChoiceField(
        label='Gender',
        choices=GENDER_CHOICES,  # Use the choices from the model
        required=False,
        widget=forms.Select(attrs={'class': 'form-select mb-0', 'aria-label': 'Gender select example'})
    )

    phone = forms.CharField(
        max_length=10,
        label='Phone',
        required=False,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='Phone number must be 10 digits.',
                code='invalid_phone_number'
            ),
        ],
        widget=forms.TextInput(attrs={'type': 'tel', 'class': 'form-control', 'placeholder': 'Enter your phone number'})
    )

    class Meta:
        model = Profile
        fields = ['avatar', 'dob', 'gender', 'address', 'phone', 'first_name', 'last_name']

    def save(self, commit=True):
        # Save the Profile instance
        profile = super().save(commit=False)

        # Set first_name and last_name on the User instance (if it exists)
        user = profile.user
        if user:
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.dob = self.cleaned_data['dob']
            user.gender = self.cleaned_data['gender']
            user.address = self.cleaned_data['address']
            user.phone = self.cleaned_data['phone']
            if commit:
                user.save()

        if commit:
            profile.save()

        return profile


