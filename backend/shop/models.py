from django.db import models

class Setting(models.Model):
    key = models.CharField(max_length=100, primary_key=True)
    value = models.TextField(default='')
    class Meta: db_table = 'settings'

class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    image = models.CharField(max_length=500, default='')
    sort_order = models.IntegerField(default=0)
    class Meta: db_table = 'categories'; ordering = ['sort_order']

class Product(models.Model):
    slug = models.SlugField(unique=True, max_length=200)
    name = models.CharField(max_length=200)
    tagline = models.CharField(max_length=500, default='')
    price = models.FloatField(default=0)
    old_price = models.FloatField(default=0)
    weight = models.CharField(max_length=50, default='200g')
    grammage_options = models.JSONField(default=dict, blank=True)
    image = models.CharField(max_length=500, default='')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.TextField(default='')
    ingredients = models.TextField(default='')
    usage = models.TextField(default='')
    best_seller = models.BooleanField(default=False)
    new_arrival = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    class Meta: db_table = 'products'

class Bundle(models.Model):
    name = models.CharField(max_length=200)
    items = models.TextField(default='')
    price = models.FloatField(default=0)
    old_price = models.FloatField(default=0)
    save_percent = models.IntegerField(default=0)
    image = models.CharField(max_length=500, default='')
    class Meta: db_table = 'bundles'

class Testimonial(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=200, default='')
    text = models.TextField()
    rating = models.IntegerField(default=5)
    active = models.BooleanField(default=True)
    class Meta: db_table = 'testimonials'

class BlogPost(models.Model):
    slug = models.SlugField(unique=True, max_length=200)
    title = models.CharField(max_length=300)
    category = models.CharField(max_length=100, default='General')
    read_time = models.CharField(max_length=20, default='5 min')
    excerpt = models.TextField(default='')
    content = models.TextField(default='')
    image = models.CharField(max_length=500, default='')
    date = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=True)
    class Meta: db_table = 'blog_posts'

class WhyItem(models.Model):
    icon = models.CharField(max_length=50, default='leaf')
    title = models.CharField(max_length=200)
    description = models.TextField(default='')
    sort_order = models.IntegerField(default=0)
    class Meta: db_table = 'why_items'; ordering = ['sort_order']

class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50, default='')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: db_table = 'contact_messages'

class SiteRating(models.Model):
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: db_table = 'site_ratings'

class SitePage(models.Model):
    page = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=300, default='')
    subtitle = models.CharField(max_length=500, default='')
    content = models.TextField(default='')
    class Meta: db_table = 'site_pages'
