from django.db import models
import uuid
from users.models import Profile


# Create your models here.
class Project(models.Model):  # each project can have some different tags, so the relationship is many to many
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    demo_link = models.CharField(max_length=2000, null=True, blank=True)
    source_link = models.CharField(max_length=2000, null=True, blank=True)
    featured_image = models.ImageField(null=True, blank=True, default='default.jpg')
    # video_demo = models.FileField(null=True, blank=True, upload_to='demo/')

    # define a many_to_many relationship
    tags = models.ManyToManyField('Tag',
                                  blank=True)  # The tag class name must be placed between the two quotation marks
    # because it is defined below the project class.
    vote_total = models.IntegerField(default=0, null=True, blank=True)
    vote_ratio = models.IntegerField(default=0, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)

    @property
    def reviewers(self):
        """""
        The values() method returns a QuerySet containing dictionaries:
            <QuerySet [{'comment_id': 1}, {'comment_id': 2}]>

        The values_list() method returns a QuerySet containing tuples:
            <QuerySet [(1,), (2,)]>
            
        If you are using values_list() with a single field, you can use flat=True to return a QuerySet of single values
            instead of 1-tuples:
                <QuerySet [1, 2]>
        """""
        queryset = self.review_set.all().values_list('owner__id', flat=True)
        return queryset

    @property
    def get_vote_count(self):
        reviews = self.review_set.all()
        up_votes = reviews.filter(value='up').count()
        total_votes = reviews.count()
        ratio = (up_votes / total_votes) * 100

        self.vote_ratio = ratio
        self.vote_total = total_votes

        self.save()

    @property
    def image_url(self):
        try:
            url = self.featured_image.url
        except:
            url = ''
        return url

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Projects"
        ordering = ['-vote_ratio', '-vote_total', 'title']  # to sort projects by date added (- : descending)


class Review(models.Model):
    VOTE_TYPE = (
        ('up', 'Up Vote'),
        ('down', 'Down Vote')
    )
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)  # this set one to many relationship
    body = models.TextField(null=True, blank=True)
    value = models.CharField(max_length=200, choices=VOTE_TYPE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)

    def __str__(self):
        return self.value

    class Meta:
        verbose_name_plural = "Reviews"
        unique_together = [['owner', 'project']]  # to define which fields of a model should be unique


class Tag(models.Model):  # each tag can belong to some different projects, so the relationship is many to many
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Tags"
