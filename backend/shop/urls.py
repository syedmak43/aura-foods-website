from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'bundles', views.BundleViewSet)
router.register(r'testimonials', views.TestimonialViewSet)
router.register(r'blog-posts', views.BlogPostViewSet)
router.register(r'why-items', views.WhyItemViewSet)
router.register(r'settings', views.SettingViewSet)
router.register(r'contact-messages', views.ContactMessageViewSet)

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('shop/', views.shop_view, name='shop'),
    path('product/<int:pid>/', views.product_detail, name='product'),
    path('about/', views.about, name='about'),
    path('blog/', views.blog, name='blog'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('contact/', views.contact_view, name='contact'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/', views.order_confirmation, name='order_confirmation'),
    path('sitemap.xml/', views.sitemap_xml, name='sitemap'),
    path('robots.txt/', views.robots_txt, name='robots'),
    path('site-rating/', views.site_rating, name='site_rating'),

    # Admin auth
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/logout/', views.admin_logout_view, name='admin_logout'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Admin CRUD
    path('admin/product/add/', views.admin_product_add, name='admin_product_add'),
    path('admin/product/edit/<int:pid>/', views.admin_product_edit, name='admin_product_edit'),
    path('admin/product/delete/<int:pid>/', views.admin_product_delete, name='admin_product_delete'),
    path('admin/product/image/<int:pid>/', views.admin_product_image, name='admin_product_image'),
    path('admin/category/add/', views.admin_category_add, name='admin_category_add'),
    path('admin/category/edit/<int:cid>/', views.admin_category_edit, name='admin_category_edit'),
    path('admin/category/delete/<int:cid>/', views.admin_category_delete, name='admin_category_delete'),
    path('admin/category/image/<int:cid>/', views.admin_category_image, name='admin_category_image'),
    path('admin/category/<int:cid>/manage-products/', views.admin_category_manage_products, name='admin_category_manage_products'),
    path('api/category/<int:cid>/products/', views.api_category_products, name='api_category_products'),
    path('admin/testimonial/add/', views.admin_testimonial_add, name='admin_testimonial_add'),
    path('admin/testimonial/delete/<int:tid>/', views.admin_testimonial_delete, name='admin_testimonial_delete'),
    path('admin/bundle/add/', views.admin_bundle_add, name='admin_bundle_add'),
    path('admin/bundle/edit/<int:bid>/', views.admin_bundle_edit, name='admin_bundle_edit'),
    path('admin/bundle/delete/<int:bid>/', views.admin_bundle_delete, name='admin_bundle_delete'),
    path('admin/bundle/image/<int:bid>/', views.admin_bundle_image, name='admin_bundle_image'),
    path('admin/bundle/<int:bid>/manage-products/', views.admin_bundle_manage_products, name='admin_bundle_manage_products'),
    path('api/bundle/<int:bid>/products/', views.api_bundle_products, name='api_bundle_products'),
    path('api/bundle/<int:bid>/add-to-cart/', views.api_bundle_add_to_cart, name='api_bundle_add_to_cart'),
    path('api/bundle/<int:bid>/detail/', views.api_bundle_detail, name='api_bundle_detail'),
    path('admin/blog/add/', views.admin_blog_add, name='admin_blog_add'),
    path('admin/blog/delete/<int:bid>/', views.admin_blog_delete, name='admin_blog_delete'),
    path('admin/blog/image/<int:bid>/', views.admin_blog_image, name='admin_blog_image'),
    path('admin/why/edit/<int:wid>/', views.admin_why_edit, name='admin_why_edit'),
    path('admin/settings/save/', views.admin_settings_save, name='admin_settings_save'),
    path('admin/upload/image/', views.admin_upload_image, name='admin_upload_image'),
    path('admin/change-password/', views.admin_change_password, name='admin_change_password'),
    path('admin/message/delete/<int:mid>/', views.admin_message_delete, name='admin_message_delete'),
    path('admin/hero-image/', views.admin_upload_image, name='admin_hero_image'),
    path('admin/story-image/', views.admin_upload_image, name='admin_story_image'),
    path('admin/upload/', views.admin_upload_image, name='admin_upload_generic'),

    # API
    path('api/product/<int:pid>/', views.api_product_detail, name='api_product_detail'),
    path('api/', include(router.urls)),
]
