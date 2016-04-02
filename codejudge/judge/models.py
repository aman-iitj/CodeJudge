from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from ckeditor.fields import RichTextField


# Create your models here.

class AuthUserManager(BaseUserManager):
    def create_user(self, username, email, roll, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')
        
        user = self.model(username=username, email=self.normalize_email(email),)
        user.is_active = True
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password):
        user = self.create_user(username=username, email=email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Hacker(AbstractBaseUser, PermissionsMixin):
    
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', message='Only alphanumeric characters are allowed.')
    ### Redefine the basic fields that would normally be defined in User ###
    username = models.CharField(unique=True, max_length=20, validators=[alphanumeric])
    email = models.EmailField(verbose_name='email address', unique=True, max_length=255)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    roll = models.CharField(max_length=50, null=False, blank=False, default = '0')
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, null=False)
    is_staff = models.BooleanField(default=False, null=False)
    
    ### Our own fields ###
    profileImage = models.ImageField(upload_to="avatar")
    objects = AuthUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    def get_full_name(self):
        fullname = self.first_name+" "+self.last_name
        return fullname

    def get_short_name(self):
        return self.username

    def __unicode__(self):
        return self.username

class Contest(models.Model):
    contestName = models.CharField(max_length=200, unique=True, null=False)
    startTime = models.DateTimeField()
    endTime = models.DateTimeField()

    def __unicode__(self):
        return self.contestName

class Problem(models.Model):
    contest = models.ForeignKey(Contest)
    problemSetter = models.CharField(max_length=200)
    problemTitle = models.CharField(max_length=200)
    problemStatement = RichTextField(config_name='awesome_ckeditor')
    testInput = models.FileField(upload_to='testInput')
    testOutput = models.FileField(upload_to='testOutput')
    #points = models.PositiveSmallIntegerField(blank=False, default = 10)
    timeLimit = models.PositiveSmallIntegerField()
    languagesAllowed = models.CommaSeparatedIntegerField(max_length=200)
    inputFormat = RichTextField(config_name='awesome_ckeditor')
    outputFormat = RichTextField(config_name='awesome_ckeditor')
    constraints = RichTextField(config_name='awesome_ckeditor')
    sampleInput = RichTextField(config_name='awesome_ckeditor')
    sampleOutput = RichTextField(config_name='awesome_ckeditor')
    solvedBy = models.PositiveSmallIntegerField(default=0)
    
    def __unicode__(self):
        return self.problemTitle

class Language(models.Model):
    language = models.CharField(max_length=200)
    extension = models.CharField(max_length=10)

    def __unicode__(self):
       return self.language

class Solution(models.Model):
    hacker = models.ForeignKey(Hacker)
    contest = models.ForeignKey(Contest)
    problem = models.ForeignKey(Problem)
    #marks = models.PositiveSmallIntegerField()
    solution = models.FileField(upload_to='solution')
    attempts = models.PositiveSmallIntegerField()
    language = models.ForeignKey(Language)
    time = models.DecimalField(max_digits=2, decimal_places=2)
    status = models.PositiveSmallIntegerField()

    def __unicode__(self):
        return str(self.id)

class Comments(models.Model):
    commentText = models.TextField()
    hacker = models.ForeignKey(Hacker)
    contest = models.ForeignKey(Contest)
    problem = models.ForeignKey(Problem)
        
class Link(models.Model):
    LinkUrl = models.CharField(max_length=200)
    LinkDescription = models.CharField(max_length=200)

class Notification(models.Model):
    NotificationText = models.TextField()