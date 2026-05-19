from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField()
    cover_image = models.ImageField(upload_to='post_covers/', blank=True, null=True)
    date_posted = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PUBLISHED)

    class Meta:
        ordering = ['-date_posted']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('post-detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title


class ReadPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='read_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='read_by')
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'post']
        ordering = ['-read_at']

    def __str__(self):
        return f'{self.user.username} read "{self.post.title}"'


class SavedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'post']
        ordering = ['-saved_at']

    def __str__(self):
        return f'{self.user.username} saved "{self.post.title}"'


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default='Django Blog',
        help_text='Displayed in the navbar and footer.')
    tab_title = models.CharField(max_length=100, default='Django Blog',
        help_text='Used as the browser tab suffix: "Post Title | Django Blog".')
    tagline = models.CharField(max_length=200, default='Ideas worth sharing.',
        help_text='Hero heading shown to guest visitors on the homepage.')
    hero_subtext = models.TextField(
        default='A community blog where writers share stories, tutorials, and insights on any topic.',
        help_text='Supporting paragraph under the hero heading.')
    about_title = models.CharField(max_length=200, default='About Django Blog',
        help_text='Heading displayed at the top of the About page.')
    about_content = models.TextField(blank=True,
        help_text='Full body of the About page. Supports rich text (HTML).')
    posts_per_page = models.PositiveSmallIntegerField(default=5,
        help_text='Number of posts shown per page on the homepage and list views.')

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # singleton — never allow deletion

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return 'Site Settings'
