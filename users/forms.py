from django import forms
from sympy import field
from .models import Profile, DetectInfo
from django.core.validators import RegexValidator


class ProfileForm(forms.ModelForm): 
    class Meta:
        model = Profile
        fields = ['avatar', 'dob', 'gender', 'address', 'phone']
        # fields = ['avatar', 'dob', 'gender', 'address', 'phone', 'first_name', 'last_name', 'email']


     # Add first_name and last_name fields explicitly
    first_name = forms.CharField(max_length=30, label='First Name', required=False, widget=forms.TextInput(attrs={'type': 'text', 'class':'shadow-sm bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light', 'placeholder':"Enter your first name"}))
    last_name = forms.CharField(max_length=30, label='Last Name', required=False, widget=forms.TextInput(attrs={'type': 'text', 'class':'shadow-sm bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light', 'placeholder':"Enter your last name"}))
    email = forms.CharField(max_length=30, label='Email', required=False, widget=forms.TextInput(attrs={'type': 'email', 'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5  dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500', 'placeholder':"name@gmail.com"}))

    # Customizing specific fields
    avatar = forms.ImageField(label='New Avatar', required=False)
    dob = forms.DateField(label='Date of Birth', widget=forms.TextInput(attrs={'type': 'date', 'class':'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5  dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500', 'placeholder':"Select date"}), required=False)
    address = forms.CharField(max_length=255, label='Address', required=False, widget=forms.TextInput(attrs={'type': 'text', 'class':'shadow-sm bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light', 'placeholder':"Enter your home address"}))
    gender = forms.ChoiceField(
    label='Gender',
    choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
    required=False,
    widget=forms.Select(attrs={'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500', 'aria-label': 'Gender select example'})
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
        widget=forms.TextInput(attrs={'type': 'tel', 'class':'shadow-sm bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light', 'placeholder': 'Enter your phone number'})
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
    
class DetectInfoForm(forms.ModelForm):
    detect_photo = forms.ImageField(label='Choose an image', required=True)

    class Meta:
        model = DetectInfo
        fields = ['detect_photo']
     
