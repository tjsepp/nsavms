from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Field, Button, HTML, Div
from crispy_forms.bootstrap import PrependedText
from django.forms import ModelForm
from django import forms
from .models import *
from authtools.models import User
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from tinymce.widgets import TinyMCE
from django.forms.models import inlineformset_factory
from authtools.forms import UserCreationForm
from django.forms.formsets import BaseFormSet,formset_factory
from django.core.mail import EmailMessage, send_mail
from nsaEvents.models import EventTasks
import io, csv
import datetime


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_id = 'LoginForm'
        #self.helper.label_class = 'col-lg-2'
        #self.helper.field_class = 'col-lg-5'
        self.helper.layout = Layout(
            PrependedText('username','@',placeholder='email address'),
            PrependedText('password',"<span class='glyphicon glyphicon-asterisk'></span>",id="password-field", css_class="passwordfields", placeholder="password"),
            HTML('<div class="form-group"><div class="col-md-4"> </div>'),
            ButtonHolder(
                Submit('login', 'Sign in', css_class='btn btnnavy'),
              ),
            HTML('<div class="col-md-12" style="margin-left:20%; margin-top:3%"><a href="{% url \'password_recovery\' %}">Recover Password</a></div>')
        )


class PasswordChangeFormExtra(PasswordChangeForm):
    def __init__(self, *args, **kw):
        super(PasswordChangeFormExtra, self).__init__(*args, **kw)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_id = 'LoginForm'
        #self.helper.label_class = 'col-lg-2'
        #self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            PrependedText('old_password',"<span class='glyphicon glyphicon-asterisk'></span>",css_class="passwordfields", placeholder="Old Password"),
            PrependedText('new_password1',"<span class='glyphicon glyphicon-lock'></span>",css_class="passwordfields", placeholder="Old Password"),
            PrependedText('new_password2',"<span class='glyphicon glyphicon-lock'></span>",css_class="passwordfields", placeholder="Old Password"),
            HTML('<div class="form-group"><div class="col-md-4"> </div>'),
            ButtonHolder(
                Submit('submit', 'Reset', css_class='btn btnnavy'),
                HTML('<a class="btn btn-default" href="/">Cancel</a>'),
              ),
        )


class PasswordRecoveryForm(PasswordResetForm):
    def __init__(self, *args, **kw):
        super(PasswordRecoveryForm, self).__init__(*args, **kw)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_id = 'LoginForm'
        #self.helper.label_class = 'col-lg-2'
       # self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            'email',
        HTML('<div class="form-group"><div class="col-md-3"> </div>'),
            Div(
               Submit('submit', 'Reset password', css_class='btn btnnavy'),
               HTML('<a class="btn btn-default" href="{% url \'mainlogin\' %}">Cancel</a>'),
               css_class='text-left',
            )

        )
    def clean_email(self):
        try:
            return User.objects.get(email=self.cleaned_data['email'])
        except User.DoesNotExist:
            raise forms.ValidationError("Can't find user based on email")
        return self.cleaned_data['email']

    def reset_email(self):
        user = self.cleaned_data['email']

        password = User.objects.make_random_password(8)
        user.set_password(password)
        user.save()

        body = """
        Sorry you are having issues with your account. Below is your username and new password:
        Username:{username}
        Password:{password}
        You can login here:http://www.nsavms.com/login/
        Change your password here:http://www.nsavms.com/changePassword/
        """.format(username = user.email, password=password)

        email = EmailMessage(
            '[NSA VMS] Password Reset', body, 'no-reply@nsavms.com',
            [user.email])
        email.send()


class AuthUserUpdateForm(ModelForm):
    class Meta:
        model = User
        fields='__all__'
    def __init__(self, *args, **kwargs):
        super(AuthUserUpdateForm,self).__init__(*args, **kwargs)


class UserProfileForm(ModelForm):
    class Meta:
        model = VolunteerProfile
        fields='__all__'

    def __init__(self, *args, **kwargs):
        super(UserProfileForm,self).__init__(*args, **kwargs)
        self.fields['interest'].queryset = VolunteerInterests.objects.filter(active=True).all()
        self.fields['interest'].widget = forms.CheckboxSelectMultiple()
        self.helper = FormHelper(self)
        self.helper.form_class='form-horizontal'
        self.helper.form_class='volunteerProfile'
        self.helper.form_id='volunteerProfileForm'
        #self.helper.label_class='col-md-2'
        #self.helper.field_class='col-md-5'
        self.helper.layout = Layout(

            Div(
            Div('firstName',css_class='col-md-6',),
            Div('lastName',css_class='col-md-6',),
            css_class='row',
            ),
            Div(
            Div('volunteerType',css_class='col-md-6',),
            Div('cellPhone',css_class='col-md-6',),
             css_class='row',
            ),
        Field('doNotEmail'),
        Field('linkedUserAccount', type="hidden"),
        HTML('<h5><b>Volunteer Interests:</b></h5>'),
        HTML("{% include 'forms/volunteerInterests.html' %}"),
        Field('interest',type='hidden'),
        Field('volStatus',type='hidden'),
        HTML('<div class="form-group"><div class="col-lg-5"></div>'),
        ButtonHolder(
        self.helper.add_input(Submit('save', 'Save', css_class="btn btnnavy")),
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))
        ))


class FamilyProfileForm(ModelForm):
    class Meta:
        model = FamilyProfile
        fields='__all__'

    def __init__(self, *args, **kwargs):
        super(FamilyProfileForm,self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class='form-horizontal'
        self.helper.form_class='volunteerProfile'
        self.helper.form_id='volunteerProfileForm'
        #self.helper.label_class='col-md-2'
        #self.helper.field_class='col-md-5'
        self.helper.layout = Layout(
        'familyName',
        'streetAddress',
        'city',
        'zip',
        'homePhone',
        'trafficRequirement',
        'volunteerRequirement',
        Field('students', type='hidden'),
        Field('specialInfo'),
        Field('inactiveDate',type='hidden'),
        Field('active',type='hidden'),
        Field('volunteers',type='hidden'),
         HTML('<div class="form-group"><div class="col-lg-5"></div>'),
        ButtonHolder(
        self.helper.add_input(Submit('save', 'Save',css_class="btn btnnavy")),
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))
        ))


class StudentUpdateForm(ModelForm):
    class Meta:
        model = Student
        fields='__all__'

    def __init__(self, *args, **kwargs):
        super(StudentUpdateForm,self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class='form-horizontal'
        self.helper.form_class='volunteerProfile'
        self.helper.form_id='volunteerProfileForm'
        self.helper.layout = Layout(
            'studentFirstName',
            'studentLastName',
            'teacher',
            'grade',
            'activeStatus',
        HTML('<div class="form-group"><div class="col-lg-5"></div>'),
        ButtonHolder(
        self.helper.add_input(Submit('save', 'Save',css_class='btn btnnavy')),
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))
        ))


class AddNewFamily(ModelForm):
    class Meta:
        model=FamilyProfile
        exclude=['volunteers', 'students']

    def __init__(self, *args, **kwargs):
        super(AddNewFamily,self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class='form-horizontal'
        self.helper.form_class='volunteerProfile'
        self.helper.form_id='volunteerProfileForm'
        self.helper.layout = Layout(
            'familyName',
            'streetAddress',
            'city',
            'zip',
            'homePhone',
            'specialInfo',
            'inactiveDate'
            'active',
            Field('trafficRequirement'),
            Field('volunteerRequirement'),
            Field('active', type='hidden'),
        HTML('<div class="form-group"><div class="col-lg-5"></div>'),
        ButtonHolder(
        self.helper.add_input(Submit('save', 'Save', css_class="btn btnnavy")),
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))
        ))


class AddFamilyVolunteers1(UserCreationForm):
    '''
    This form is for the new family initialization process. This is used to build the
    formset allowing the administrators to add several users at one time.
    '''
    def __init__(self, *args, **kwargs):
        super(AddFamilyVolunteers, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class':'form-control'})
        self.fields['password2'].help_text=None
        self.helper = FormHelper()
        self.helper.form_class='form-inline volunteerProfile'
        self.helper.form_id='volunteerProfile'
        self.helper.layout = Layout(
            'name',
            'email',
            'password1',
            'password2',
            )
    def clean_email(self):
        try:
            User.objects.get(email = self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError('This email is already in use. Please check for existing user')

class AddFamilyVolunteers(UserCreationForm):
    '''
    This form is for the new family initialization process. This is used to build the
    formset allowing the administrators to add several users at one time.
    '''
    cell_phone = forms.CharField(max_length=15, required=False)
    vol_type = forms.ModelChoiceField(queryset=VolunteerType.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super(AddFamilyVolunteers, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class':'form-control'})
        self.autoPassword = User.objects.make_random_password(8)
        self.fields['password2'].help_text=None
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        self.helper = FormHelper()
        self.helper.form_class='form-inline volunteerProfile'
        self.helper.form_id='volunteerProfile'
        self.helper.layout = Layout(
            'name',
            'email',
            'cell_phone',
            'vol_type',
            'password1',
            'password2',
            )
    def clean_email(self):
        try:
            User.objects.get(email = self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError('This email is already in use. Please check for existing user')
    '''
    def clean_password2(self):
        password1 = self.autoPassword
        password2 = self.autoPassword
        super(AddFamilyVolunteers, self)
    '''

    def send_welcome_email(self,email,name,password):
        body = """
        Hi {name},
        You have been added to the North Star Academy volunteer management system.
        Here is your login information:
        Username:{username}
        Password:{password}

        You can login at: http://www.nsavms.com/login/
        Once logged in, we recommend you change your password using this link: http://www.nsavms.com/changePassword/
        """.format(username = email,name = name,password=password)

        email = EmailMessage(
            '[NSA VMS] Account Creation', body, 'no-reply@nsavms.com',
            [email])
        email.send()

    def save(self, commit=True):
        self.cleaned_data['password1']= self.autoPassword
        self.cleaned_data['password2']=self.autoPassword
        user = super(AddFamilyVolunteers,self).save(commit=True)
        user.save()
        profile = VolunteerProfile.objects.get_or_create(linkedUserAccount=user.id)[0]
        profile.cellPhone = self.cleaned_data['cell_phone']
        profile.save()
        self.send_welcome_email(user.email,profile.firstName,self.autoPassword)
        return user,profile



class AddNewVolunteersToFamily(UserCreationForm):
    '''
    This form is for inputting users into existing Families.
    '''
    def __init__(self, *args, **kwargs):
        super(AddNewVolunteersToFamily, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class':'form-control'})
        self.fields['password2'].help_text=None
        self.helper = FormHelper()
        self.helper.form_class='form-horizontal'
        self.helper.form_id='volunteerProfile'
        self.helper.layout = Layout(
            'name',
            'email',
            'password1',
            'password2',
            )
        ButtonHolder(
        self.helper.add_input(Submit('save', 'Save', css_class="btn btnnavy")),
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))
        )
    def clean_email(self):
        try:
            User.objects.get(email = self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError('This email is already in use. Please check for existing user')

class userFormTest(forms.ModelForm):
    class Meta:
        model = User



class AddUserEventForm(ModelForm):
    class Meta:
        model = VolunteerHours
        fields = '__all__'


    def __init__(self, *args, **kwargs):
        self.famcount = len(kwargs.pop('famcount'))
        self.user= kwargs.pop('user')
        super(AddUserEventForm,self).__init__(*args, **kwargs)
        self.fields['family'].queryset = FamilyProfile.objects.filter(famvolunteers = self.user)
        self.fields['event'].queryset = NsaEvents.objects.filter(allowView=True)
        self.fields['schoolYear'].initial = SchoolYear.objects.get(currentYear = 1).yearId
        if self.famcount==1:
            self.fields['family'].initial = FamilyProfile.objects.get(famvolunteers=self.user)
        self.helper = FormHelper(self)
        self.helper.form_class='form-horizontal'
        self.helper.form_class='volunteerProfile'
        self.helper.form_id='volunteerProfileForm'

        self.helper.layout = Layout(
            Field('eventDate', css_class='datepicker',placeholder='Select Date'),
            Field('event',css_class='select2It'),
            Field('task', css_id='task', css_class='typeahead'),
            Field('volunteer',type='hidden'),
            #Field('family', type='hidden'),
            Field('volunteerHours',placeholder='Enter Number Of Hours'),
                  HTML(
                """
                <div class="row timeEntry">
                    <div class="col-lg-6">
                        <div class="input-group bootstrap-timepicker timepicker">
                        <input id="timepicker1" type="text" class="form-control input-small" placeholder="Start Time">
                        <span class="input-group-addon"><i class="glyphicon glyphicon-time"></i></span>
                    </div>
                </div>
                <div class="col-lg-6">
                    <div class="input-group bootstrap-timepicker timepicker-orient-bottom">
                        <input id="timepicker2" type="text" class="form-control input-small" placeholder="End Time">
                        <span class="input-group-addon"><i class="glyphicon glyphicon-time" id='pickIcon2'></i></span>
                    </div>
                </div>
                <div class='col-md-12' style='color:red; display: none; margin-bottom:2%' id='dataWarning'></div>
                </div>
            """
            ),
            Field('schoolYear',type='hidden'),
        ButtonHolder(
        self.helper.add_input(Submit('save', 'Save', css_class="btn btnnavy")),
        self.helper.add_input(Submit('saveAndAdd', 'Save & Add Another', css_class="btn btnnavy")),
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))
        ))
        if self.famcount>1:
            self.helper.layout.append(Field('family',css_id='LogHoursFamily'))

        else:
            self.helper.layout.append(Field('family',type='hidden'))
        self.helper.layout.append(HTML('<div class="form-group"><div class="col-lg-5"></div>'))


class AddInterestForm(ModelForm):
    class Meta:
        model=VolunteerInterests

    def __init__(self, *args, **kwargs):
        super(AddInterestForm,self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class='form-horizontal'
        self.helper.form_class='volunteerProfile'
        self.helper.form_id='volunteerProfileForm'
        self.helper.layout = Layout(
            'interestName',
            'description',
            'active',
        HTML('<div class="form-group"><div class="col-lg-5"></div>'),
        ButtonHolder(
        self.helper.add_input(Submit('save', 'Save', css_class="btn btnnavy")),
        self.helper.add_input(Submit('saveAndAdd', 'Save & Add Another', css_class="btn btnnavy")),
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))
        ))

class RecruitingEmailForm(forms.Form):
    subject = forms.CharField(max_length=100, label='Subject')
    msgbody = forms.CharField(widget=forms.Textarea, label='Message')
    file = forms.FileField(widget = forms.FileInput(attrs={'name':'file'}),required=False,label='Attachement')
    def __init__(self,*args, **kwargs):
        super(RecruitingEmailForm,self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class='form-horizontal'
        self.helper.form_class='volunteerProfile'
        self.helper.form_id='volunteerProfileForm'
        self.helper.layout = Layout(
            HTML('''
                 <div class="panel panel-default">
                <div class="panel-heading">Sending Email To:</div>
                <div class="panel-body">
                                {%for x in volNames %}
                    <i class='emailnames'>{{ x.name }}</i>
                    {% if forloop.last %}
                    {% else %}
                    ,
                    {% endif %}
                {% endfor %}
                </div>
                </div>
            '''),
            'subject',
            'msgbody',
            'file'
        )
        self.helper.add_input(Submit('submit','Send Email'))
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))


class EditVolunteersLogin(AuthUserUpdateForm):
    '''
    This form is for inputting users into existing Families.
    '''
    def __init__(self, *args, **kwargs):
        super(EditVolunteersLogin, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class':'form-control'})

        self.helper = FormHelper()
        self.helper.form_class='form-horizontal'
        self.helper.form_id='volunteerProfile'
        self.helper.layout = Layout(
            'name',
            'email',
            Field('is_superuser', type='hidden'),
            Field('is_staff', type='hidden'),
            Field('is_active', type="hidden"),
            Field('password', type="hidden"),
            Field('date_joined', type="hidden"),
            Field('last_login', type="hidden"),
            Field('groups', type='hidden'),
            Field('user_permissions', type="hidden")
            )
        ButtonHolder(
        self.helper.add_input(Submit('save', 'Save', css_class="btn btnnavy")),
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))
        )

class TrafficWeeklyUpdate(ModelForm):
    class Meta:
        model=Traffic_Duty
    weekPicker = forms.CharField(label='Week')
    def __init__(self, *args, **kwargs):
        super(TrafficWeeklyUpdate,self).__init__(*args, **kwargs)
        self.fields['schoolYear'].initial = SchoolYear.objects.get(currentYear = 1).yearId
        self.fields['volunteerId'].queryset = User.objects.filter(is_active = True)
        self.helper = FormHelper(self)
        self.helper.form_class='form-horizontal'
        self.helper.form_class='volunteerProfile'
        self.helper.form_id='volunteerProfileForm'
        self.helper.layout = Layout(
            Field('volunteerId',css_class='selectVol'),
            'linkedFamily',
            Field('schoolYear',type='hidden'),
            Div(
            Field('weekPicker',id='weeklyDatePicker'),style='position: relative'),
            Field('weekStart',type="hidden"),
            Field('weekEnd',type="hidden"),
            Field('morning_shifts',css_class='shifts',id='amShifts'),
            Field('afternoon_shifts',css_class='shifts',id='pmShifts'),
            Field('totalTrafficShifts',id='totalShifts'),
            Field('volunteerHours',css_class='volunteerHours',id='volunteerHours'),
            Field('am_manager',css_class='check_class', id='supervisor'),
            Field('kindie',css_class='check_class',id='kindie'),
        HTML('<div class="form-group"><div class="col-lg-5"></div>'),
        ButtonHolder(
        self.helper.add_input(Submit('save', 'Save', css_class="btn btnnavy")),
        self.helper.add_input(Submit('saveAndAdd', 'Save & Add Another', css_class="btn btnnavy")),
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))
        ))

class DeclineLoggedHours(forms.Form):
    subject = forms.CharField(max_length=100, label='Subject')
    msgbody = forms.CharField(widget=forms.Textarea, label='Message')
    def __init__(self,*args, **kwargs):
        super(DeclineLoggedHours,self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class='form-horizontal'
        self.helper.form_class='volunteerProfile'
        self.helper.form_id='volunteerProfileForm'
        self.helper.layout = Layout(
            HTML('''
               <div class="panel panel-default">
                <div class="panel-heading">Volunteer Detail:</div>
                <div class="panel-body">
                <p><b>Volunteer: </b>{{volDetail.volunteer.name}}</p>
                <p><b>Event: </b>{{volDetail.event.eventName}}</p>
                <p><b>Volunteer Date: </b>{{volDetail.eventDate}}</p>
                <p><b>Date Entered: </b>{{volDetail.dateCreated}}</p>
                <p><b>Task: </b>{{volDetail.task}}</p>
                <p><b>Volunteer Hours: </b>{{volDetail.volunteerHours}}</p>
                </div>
               </div>
            '''),
            'subject',
            'msgbody',
        )
        self.helper.add_input(Submit('submit','Send Email'))
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))



class upLoadRewardCardUsers(forms.Form):
    data_file = forms.FileField(widget = forms.FileInput(attrs={'name':'file'}),required=False,label='Reward Card User Upload')

    def __init__(self,*args, **kwargs):
        super(upLoadRewardCardUsers,self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class='form-horizontal'
        self.helper.form_class='volunteerProfile'
        self.helper.form_id='volunteerProfileForm'
        self.helper.layout = Layout(
            'data_file',
        )
        self.helper.add_input(Submit('submit','Add Cards'))
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))

    def process_data(self):
        """
        take csv with header:user,family,store,cardNumber
        """
        errorRecs = []
        f = io.TextIOWrapper(self.cleaned_data['data_file'].file)
        reader = csv.DictReader(f)

        for card in reader:
            try:
                RewardCardUsers.objects.get_or_create(linkedUser = User.objects.get(pk=card['user'])
                                            ,family=FamilyProfile.objects.get(pk=card['family'])
                                            ,storeName=card['store'],customerCardNumber=card['cardNumber'])
            except:
                errorRecs.append(card)
        if len(errorRecs)>0:
            print card


class AddEditRewardCardUsers(ModelForm):
    '''
    This class allows admins to log volunteer hours from events
    '''
    class Meta:
        model = RewardCardUsers
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AddEditRewardCardUsers,self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class='form-horizontal'
        self.helper.form_class='volunteerProfile'
        self.helper.form_id='volunteerProfileForm'

        self.helper.layout = Layout(
            Field('linkedUser',lable='Volunteer', css_class ='volunteerSelect', id='id_volunteerId'),
            Field('family',id='id_linkedFamily'),
            Field('storeName', lable='Store'),
            Field('customerCardNumber', css_id='cardNumber',lable='Card Number'),
            Field('active'),
            Field('lastReportedUsage', type='hidden'),
        ButtonHolder(
        self.helper.add_input(Submit('save', 'Save', css_class="btn btnnavy")),
        self.helper.add_input(Submit('saveAndAdd', 'Save & Add Another', css_class="btn btnnavy")),
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))
        ))



class AddEditRewardCardData(ModelForm):
    '''
    This class allows admins to log volunteer hours from events
    '''
    class Meta:
        model = RewardCardUsage
        fields = '__all__'
        widgets ={
            'customerCardNumber':forms.Select(),
        }
    def __init__(self, *args, **kwargs):
        #self.famcount = len(kwargs.pop('famcount'))
        #self.user= kwargs.pop('user')
        super(AddEditRewardCardData,self).__init__(*args, **kwargs)
        #self.fields['event'].queryset = NsaEvents.objects.filter(allowView=True)
        self.fields['schoolYear'].initial = SchoolYear.objects.get(currentYear = 1).yearId
        self.helper = FormHelper(self)
        self.helper.form_class='form-horizontal'
        self.helper.form_class='volunteerProfile'
        self.helper.form_id='volunteerProfileForm'

        self.helper.layout = Layout(
            Field('volunteerId', css_class ='volunteerSelect', css_id='id_volunteer'),
            #Field('linkedFamily',),
            Field('customerCardNumber', css_id='cardNumber'),
            Field('refillDate', css_class='datepicker',placeholder='Select Date'),
            Field('refillValue', css_class='refillValue', placeholder ='Enter dollar amount'),
            Field('volunteerHours', type='hidden'),
            Field('storeName', type='hidden'),
            Field('schoolYear', type='hidden'),
        ButtonHolder(
        self.helper.add_input(Submit('save', 'Save', css_class="btn btnnavy")),
        self.helper.add_input(Submit('saveAndAdd', 'Save & Add Another', css_class="btn btnnavy")),
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))
        ))





def convertKSNumbers(num):
    digs = num.split('-')[-3:]
    dig2 = ''.join(digs)
    finalVal = ' '.join(dig2[i:i+3] for i in xrange(0,len(dig2),3))
    return finalVal


class upLoadRewardCardPurchaseData(forms.Form):
    data_file = forms.FileField(widget = forms.FileInput(attrs={'name':'file'}),required=False,label='Reward Card Purchase Data')

    def __init__(self,*args, **kwargs):
        super(upLoadRewardCardPurchaseData,self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class='form-horizontal'
        self.helper.form_class='volunteerProfile'
        self.helper.form_id='volunteerProfileForm'
        self.helper.layout = Layout(
            'data_file',
        )
        self.helper.add_input(Submit('submit','Add Data',css_class='btn-btnnavy'))
        self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-default', onclick="window.history.back()"))

    def process_data(self):
        """
        take csv with header:user,family,store,cardNumber
        """
        errorRecs = []
        f = io.TextIOWrapper(self.cleaned_data['data_file'].file)
        reader = csv.DictReader(f)


        for data in reader:
            data['store']='King Soopers'
            prop_date =datetime.datetime.strftime(datetime.datetime.strptime(data['date'],'%m/%d/%Y'),'%Y-%m-%d')
            if data['store']=='King Soopers':
                card_num = convertKSNumbers(data['cardnumber'])
            else:
                card_num=data['cardnumber']

            #when procesing the kingsoopers csv, sometimes negat
            if '(' and ')' in data['value']:
                print 'this is a negative value'
                cardVal= float(data['value'].replace('(','').replace(')','').replace('$','-'))
            else:
                cardVal = float(data['value'].replace('$',''))

            if cardVal>0:
                try:
                    RewardCardUsage.objects.create(customerCardNumber = card_num,refillValue=cardVal,
                                                      refillDate=prop_date,storeName=data['store'],schoolYear=SchoolYear.objects.get(currentYear=1),
                                                      statementCardNumber=data['cardnumber'])
                except:
                    pass
