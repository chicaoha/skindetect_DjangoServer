import email
from django import forms
from .models import Profile, DetectInfo  
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class ProfileForm(forms.ModelForm): 
    class Meta:
        model = Profile
        fields = ['avatar', 'dob', 'gender', 'address', 'phone']

    first_name = forms.CharField(max_length=30, label='First Name', required=False, widget=forms.TextInput(attrs={'type': 'text', 'class': 'w-full rounded-md border border-stroke bg-white py-3 px-6 text-base font-medium text-body outline-none focus:border-primary focus:shadow-input dark:border-stroke-dark dark:bg-black dark:text-white dark:focus:border-primary', 'placeholder': "Enter your first name"}))
    last_name = forms.CharField(max_length=30, label='Last Name', required=False, widget=forms.TextInput(attrs={'type': 'text', 'class': 'w-full rounded-md border border-stroke bg-white py-3 px-6 text-base font-medium text-body outline-none focus:border-primary focus:shadow-input dark:border-stroke-dark dark:bg-black dark:text-white dark:focus:border-primary', 'placeholder': "Enter your last name"}))
    email = forms.CharField(label='Email', required=False, widget=forms.TextInput(attrs={'type': 'email', 'class': 'w-full rounded-md border border-stroke bg-white py-3 px-6 text-base font-medium text-body outline-none focus:border-primary focus:shadow-input dark:border-stroke-dark dark:bg-black dark:text-white dark:focus:border-primary', 'placeholder': "name@gmail.com"}))

    avatar = forms.ImageField(label='New Avatar', required=False)
    dob = forms.DateField(label='Date of Birth', widget=forms.TextInput(attrs={'type': 'date', 'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5  dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500', 'placeholder': "Select date"}), required=False)
    address = forms.CharField(max_length=255, label='Address', required=False, widget=forms.TextInput(attrs={'type': 'text', 'class': 'shadow-sm bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light', 'placeholder': "Enter your home address"}))
    gender = forms.ChoiceField(label='Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], required=False, widget=forms.Select(attrs={'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500', 'aria-label': 'Gender select example'}))
    phone = forms.CharField(max_length=10, label='Phone', required=False, validators=[RegexValidator(regex=r'^\d{10}$', message='Phone number must be 10 digits.', code='invalid_phone_number')], widget=forms.TextInput(attrs={'type': 'tel', 'class': 'shadow-sm bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light', 'placeholder': 'Enter your phone number'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user = self.instance.user  # Get the user associated with the profile instance
        
        # Check if the email has changed
        if email != user.email:
            # Check if the new email is already in use by another user
            if User.objects.filter(email=email).exists():
                raise ValidationError("This email is already in use.")
        
        return email
    
    def save(self, commit=True):
        profile = super().save(commit=False)
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
    
class DetectInfoForm(forms.ModelForm):
    detect_photo = forms.ImageField(label='Choose an image', required=True)

    class Meta:
        model = DetectInfo
        fields = ['detect_photo']
