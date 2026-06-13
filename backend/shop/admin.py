from django.contrib import admin
from .models import Product, Category, Bundle, Testimonial, BlogPost, WhyItem, Setting, ContactMessage

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'best_seller', 'active']
    list_filter = ['category', 'best_seller', 'new_arrival']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'sort_order']

@admin.register(Bundle)
class BundleAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'save_percent']

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'rating', 'active']

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'date', 'active']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(WhyItem)
class WhyItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'sort_order']

@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'value']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at']
    readonly_fields = ['name', 'email', 'phone', 'message', 'created_at']
