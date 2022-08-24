from django.db import models
from io import BytesIO
from django.core.files import File
from django.contrib.auth.models import AbstractUser, UserManager
from users.models import CustomUser, Profile
from PIL import Image
from django.utils.text import slugify
from django.conf import settings
from django.db.models import Q


BASE_RATING = (
    (1, "Needs major improvements"),
    (2, "You could've done better"),
    (3, "I think you nailed it"),
    (4, "Better than I expected"),
    (5, "I think you excel in this area"),
)


# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=254, unique=True) # MySQL may not allow unique CharFields to have a max_length > 255.
    slug = models.SlugField(unique=True, blank=True)    # auto generated slug using slugify

    class Meta:
        # With ordering we will be able to see all the categories arranged
        ordering = ('name',)
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/{self.slug}/' # Missing trailing /

    def _get_unique_slug(self):
        slug = slugify(self.name)
        unique_slug = slug
        number = 1
        while Category.objects.filter(slug=unique_slug).exists():
            unique_slug = f'{slug}-{number}'    # This way we can have a unique slug for every category
            number += 1
        return unique_slug

    # upon saving the Category
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save(*args, **kwargs)


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=254, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    actual_product = models.URLField(max_length=750)    # House the link for the ACTUAL product from online stores
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='product_image/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='product_thumbnail/', blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        # This is going to order our products from the most recent date that the product was added
        ordering = ('-date_added',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/{self.category.slug}/{self.slug}/'

    def get_image(self):
        if self.image:
            return self.image.url
        else:
            return ''

    def get_image_name(self):
        if self.image:
            image_split = self.image.url.split('/')     # [https,'', storage, powerpetpro, product_image, img_name]
            return image_split[-1]  # we'll get that last img_name
        else:
            return ""

    def get_thumbnail(self):
        # We want to make sure the thumbnail matches with the images in case the image is updated
        if self.thumbnail:  # if theres a thumbnail then we could set the tumbnail name
            thumbnail_name = self.thumbnail.name.split('/')[-1]
        # first we are going to make sure the thumbnail picture is the same name as our image
        if self.thumbnail and thumbnail_name == self.get_image_name:
            return self.thumbnail.url
        else:
            if self.image:
                # Our function make_thumbnail will use pillow etc to resize
                self.thumbnail = self.make_thumbnail(self.image)
                self.save()

                return self.thumbnail.url
            else:
                return ''

    def make_thumbnail(self, image, size=(300, 300)):
        img = Image.open(image)
        # We are going to convert to RGB to make sure everything is fine
        img.convert('RGB')
        # then we are going to use Image's thumbnail function given our default size of 300 width x 200 height
        img.thumbnail(size)

        # We are going to use BytesIO to save our image as bytes
        thumb_io = BytesIO()
        img.save(thumb_io, 'png', quality=85)

        # We need to construct a File object ourselves
        thumbnail = File(thumb_io, name=image.name)

        return thumbnail

    def _get_unique_slug(self):
        slug = slugify(self.name)
        unique_slug = slug
        number = 1
        while Product.objects.filter(slug=unique_slug).exists():
            unique_slug = f'{slug}-{number}'
            number += 1
        return unique_slug

    def get_short_description(self):
        # We are going to return the first 100 characters
        short_description = self.description[:101]

        if len(short_description) >= 100:
            return f'{short_description}...'
        else:
            return short_description

    # upon saving the Product
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save(*args, **kwargs)


class MessageBox(models.Model):
    msg = models.CharField(max_length=254, unique=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Message Boxes'
        ordering = ('-date_added',)

    def __str__(self):
        return self.msg


class MissionStatement(models.Model):
    main_statement = models.TextField(max_length=800)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Mission Statements'
        ordering = ('-date_added',)

    def __str__(self):
        return self.main_statement


# We are going to use this to split up our mission statement into more detailed explanations on specific topics
class MissionStatementTopics(models.Model):
    topic = models.CharField(max_length=254, unique=True)
    date_added = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = 'Mission Statement Topics'

    def __str__(self):
        return self.topic

    def _get_unique_slug(self):
        slug = slugify(self.topic)
        unique_slug = slug
        number = 1
        while MissionStatementTopics.objects.filter(slug=unique_slug).exists():
            unique_slug = f'{slug}-{number}'
            number += 1
        return unique_slug

    def save(self, *args, **kwargs):
        # If we don't have a slug then we will make one
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save(*args, **kwargs)


# Our mission details will just include all the information for a specific mission statement topic
class MissionDetails(models.Model):
    # We are building this logic similar to a Topic/Entry model
    mission_topic = models.ForeignKey(MissionStatementTopics, on_delete=models.CASCADE)
    mission_topic_details = models.TextField(max_length=800)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Mission Statement Topic Details'
        ordering = ('-date_added',)

    def __str__(self):
        return f'{self.mission_topic}: {self.mission_topic_details[:30]}'


# Obtain Feedback from our users
# Adding questions
class FeedBackQuestions(models.Model):
    questions = models.CharField(max_length=500)

    class Meta:
        verbose_name_plural = "Questions"

    def get_answer_choices(self):
        return BASE_RATING

    def __str__(self):
        return 'Question: %s' % self.questions


class Feedback(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    # since we have profile we could do Profile.feedback_set.first() to get the first/only feedback w/ profile model
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True)
    opinions = models.TextField(max_length=500)
    suggestions = models.TextField(max_length=500)
    date_submitted = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_submitted']

    def get_grading_rule(self):
        return BASE_RATING

    def __str__(self):
        if self.user:
            return f'{self.user.username}: "{self.opinions[:50]}"'
        else:
            return f'Anonymous User: "{self.opinions[:50]}"'


class FeedBackAnswers(models.Model):
    """"
        user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
            So we actually don't need user because we already have Feedback as our foreign key
            If we leave user with a one-to-one field then we could only submit ONE question for ONE user
                That's not what we want
    """
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE)  # we are going to tie it to one Feedback model
    # if answer exist then they can't answer again.
    """
        question = models.OneToOneField(FeedBackQuestions, on_delete=models.CASCADE)
        
        We can't use OneToOne field because one record of the question cannot relate to one record of answer 
        What happens is you'll get '"question": ["This field must be unique."]' because you've submitted multiple ans
        to just one question even with a different feedback pk
        
        Problem: Unique=False which means someone could submit another answer for the same question in the same feedback
        Solution: Handle this with .exists()
    """
    question = models.ForeignKey(FeedBackQuestions, on_delete=models.CASCADE, unique=False)
    # We could access answers based on feedback with Feedback.feedbackanswers_set.all() ## modelname_set.all()
    answer = models.IntegerField(choices=BASE_RATING, default=1)

    class Meta:
        verbose_name_plural = "Answers"

    def get_written_ans(self):
        # NOTE that BASE_ANSWER is a tuple so we could search using index but note that index starts at 0
        return BASE_RATING[self.answer-1][1]    # this '1' means we are getting the written in (num, written)

    def get_score(self):
        return BASE_RATING[self.answer-1][0]    # this '0' means we are getting the num in (num, written)

    def __str__(self):
        return f'(Feedback#{self.feedback.id}) Question#{self.question.id} Answer: {self.answer}'


class SubmitBug(models.Model):
    # Bug owner is not necessary because anyone could add it
    bug_owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True, unique=False)
    # but Bug Owner name is required we need to at least know WHO sent this
    bug_owner_name = models.CharField(max_length=100, blank=False, null=False)
    bug_message = models.TextField(max_length=500)
    bug_image = models.ImageField(upload_to='product_image/', blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date_added',)    # We will see the most recent bug submitted the users

    def __str__(self):
        return f'Bug Name-ID: {self.bug_owner_name}-{self.id}'