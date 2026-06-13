from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Product, Category, Bundle, Testimonial, BlogPost, WhyItem, Setting, ContactMessage, SiteRating
from .serializers import (ProductSerializer, CategorySerializer, BundleSerializer, TestimonialSerializer, BlogPostSerializer, WhyItemSerializer, SettingSerializer, ContactMessageSerializer)

# ===== PUBLIC VIEWS =====
def seo_context(title, desc, url, image='/static/images/hero-spices.jpg'):
    return {'meta':{'title':f'{title} — Aura Foods','description':desc,'url':url,'image':image}}

def home(request):
    products = Product.objects.filter(active=True).order_by('-featured')
    cats = Category.objects.all()
    best_sellers = [p for p in products if p.best_seller][:4]
    ctx = seo_context('Aura Foods — Pure & Premium Organic Spices of Pakistan','Freshly packed authentic spices from the fields of Sindh, delivered across Pakistan.','https://aurafoods.pk/')
    testimonials = Testimonial.objects.filter(active=True)
    ratings = SiteRating.objects.all()
    avg_rating = round(sum(r.rating for r in ratings) / len(ratings), 1) if ratings else 0
    ctx.update({'products':products[:8],'best_sellers':best_sellers,'categories':cats_with_slugs(cats),'testimonials':testimonials[:3],'bundles':Bundle.objects.all(),'why_items':WhyItem.objects.all(),'settings':{s.key:s.value for s in Setting.objects.all()},'site_rating_avg':avg_rating,'site_rating_count':len(ratings)})
    return render(request, 'index.html', ctx)

def shop_view(request):
    cat_slug = request.GET.get('category')
    products = Product.objects.filter(active=True).order_by('-featured')
    if cat_slug:
        products = products.filter(category__name__iexact=cat_slug.replace('-',' '))
    ctx = seo_context('Shop Organic Spices','Browse our complete range of pure, organic Pakistani spices.','https://aurafoods.pk/shop')
    ctx.update({'products':products,'categories':cats_with_slugs(Category.objects.all())})
    return render(request, 'shop.html', ctx)

def product_detail(request, pid):
    product = get_object_or_404(Product, id=pid, active=True)
    related = Product.objects.filter(category=product.category, active=True).exclude(id=pid)[:4]
    ctx = seo_context(product.name, product.tagline, f'https://aurafoods.pk/product/{pid}', product.image)
    ctx.update({'product':product,'related':related})
    return render(request, 'product.html', ctx)

def about(request):
    settings = {s.key:s.value for s in Setting.objects.all()}
    ctx = seo_context('About Aura Foods','Learn the story behind Pakistan\'s premium organic spice brand.','https://aurafoods.pk/about')
    ctx.update({'settings':settings,'why_items':WhyItem.objects.all()})
    return render(request, 'about.html', ctx)

def blog(request):
    posts = BlogPost.objects.filter(active=True).order_by('-date')
    ctx = seo_context('Blog — Aura Foods','Read about spices, recipes, and Pakistani culinary heritage.','https://aurafoods.pk/blog')
    ctx.update({'posts':posts})
    return render(request, 'blog.html', ctx)

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, active=True)
    other = BlogPost.objects.filter(active=True).exclude(slug=slug)[:3]
    ctx = seo_context(post.title, post.excerpt, f'https://aurafoods.pk/blog/{slug}', post.image)
    ctx.update({'post':post,'other_posts':other})
    return render(request, 'blog_detail.html', ctx)

def site_rating(request):
    r = request.GET.get('rating') or request.POST.get('rating')
    if r and r.isdigit() and 1 <= int(r) <= 5:
        SiteRating.objects.create(rating=int(r))
    return redirect(request.META.get('HTTP_REFERER', '/'))

def contact_view(request):
    settings = {s.key:s.value for s in Setting.objects.all()}
    ctx = seo_context('Contact Aura Foods','Reach out for orders, wholesale inquiries, or any questions.','https://aurafoods.pk/contact')
    ctx.update({'settings':settings})
    if request.method == 'POST':
        ContactMessage.objects.create(
            name=request.POST.get('name',''),
            email=request.POST.get('email',''),
            phone=request.POST.get('phone',''),
            message=request.POST.get('message','')
        )
        ctx['success'] = "Thank you! We'll get back to you within 24 hours."
    return render(request, 'contact.html', ctx)

def cart(request):
    return render(request, 'cart.html', seo_context('Cart — Aura Foods','','https://aurafoods.pk/cart'))

def checkout(request):
    return render(request, 'checkout.html', seo_context('Checkout — Aura Foods','','https://aurafoods.pk/checkout'))

def order_confirmation(request):
    return render(request, 'order_confirmation.html', seo_context('Order Confirmed — Aura Foods','','https://aurafoods.pk/order-confirmation'))

def sitemap_xml(request):
    products = Product.objects.filter(active=True)
    posts = BlogPost.objects.filter(active=True)
    return render(request, 'sitemap.xml', {'products':products,'posts':posts}, content_type='application/xml')

def robots_txt(request):
    return render(request, 'robots.txt', content_type='text/plain')

def handler404(request, exception):
    return render(request, '404.html', status=404)

# ===== ADMIN AUTH =====
def admin_login(request):
    if request.user.is_authenticated:
        return redirect('/admin/dashboard/')
    error = None
    if request.method == 'POST':
        user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
        if user:
            login(request, user)
            return redirect('/admin/dashboard/')
        else:
            error = 'Invalid credentials'
    return render(request, 'admin/login.html', {'error':error})

@login_required
def admin_logout_view(request):
    logout(request)
    return redirect('/admin/login/')

@login_required
def admin_dashboard(request):
    products = Product.objects.filter(active=True)
    category_products = {}
    for c in Category.objects.all():
        category_products[c.id] = products.filter(category=c)
    ctx = {
        'products': products,
        'recent_products': products[:5],
        'categories': Category.objects.all(),
        'category_products': category_products,
        'testimonials': Testimonial.objects.filter(active=True),
        'bundles': Bundle.objects.all(),
        'blog_posts': BlogPost.objects.filter(active=True),
        'why_items': WhyItem.objects.all(),
        'messages': ContactMessage.objects.all().order_by('-created_at'),
        'settings': {s.key:s.value for s in Setting.objects.all()},
    }
    return render(request, 'admin/dashboard.html', ctx)

# ===== ADMIN CRUD HELPERS =====
def slugify(text):
    import re
    s = str(text).lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s

def cats_with_slugs(cats):
    return [{'id':c.id,'name':c.name,'image':c.image,'slug':slugify(c.name),'count':c.product_set.filter(active=True).count()} for c in cats]

@csrf_exempt
@login_required
def admin_product_add(request):
    if request.method == 'POST':
        grammage = {}
        for g in ('100','250','500','1000'):
            v = request.POST.get(f'gram_{g}')
            if v and float(v) > 0:
                grammage[g] = float(v)
        Product.objects.create(
            slug=slugify(request.POST.get('name','')),
            name=request.POST.get('name',''),
            tagline=request.POST.get('tagline',''),
            price=float(request.POST.get('price',0)),
            old_price=float(request.POST.get('old_price',0)),
            weight=request.POST.get('weight','200g'),
            grammage_options=grammage,
            category_id=int(request.POST.get('category_id',1)),
            description=request.POST.get('description',''),
            ingredients=request.POST.get('ingredients',''),
            usage=request.POST.get('usage',''),
            best_seller=bool(int(request.POST.get('best_seller',0))),
            new_arrival=bool(int(request.POST.get('new_arrival',0))),
        )
    return redirect('/admin/dashboard/')

@csrf_exempt
@login_required
def admin_product_edit(request, pid):
    if request.method == 'POST':
        p = get_object_or_404(Product, id=pid)
        p.slug = slugify(request.POST.get('name',p.name))
        p.name = request.POST.get('name',p.name)
        p.tagline = request.POST.get('tagline',p.tagline)
        p.price = float(request.POST.get('price',p.price))
        p.old_price = float(request.POST.get('old_price',p.old_price))
        p.weight = request.POST.get('weight',p.weight)
        grammage = {}
        for g in ('100','250','500','1000'):
            v = request.POST.get(f'gram_{g}')
            if v and float(v) > 0:
                grammage[g] = float(v)
        p.grammage_options = grammage
        p.category_id = int(request.POST.get('category_id',p.category_id))
        p.description = request.POST.get('description',p.description)
        p.ingredients = request.POST.get('ingredients',p.ingredients)
        p.usage = request.POST.get('usage',p.usage)
        p.best_seller = bool(int(request.POST.get('best_seller',0)))
        p.new_arrival = bool(int(request.POST.get('new_arrival',0)))
        p.save()
    return redirect('/admin/dashboard/')

@csrf_exempt
@login_required
def admin_product_delete(request, pid):
    Product.objects.filter(id=pid).delete()
    return redirect('/admin/dashboard/')

@csrf_exempt
@login_required
def admin_product_image(request, pid):
    if request.method == 'POST' and request.FILES.get('file'):
        from pathlib import Path
        f = request.FILES['file']
        ext = Path(f.name).suffix or '.jpg'
        fname = f'product_{pid}{ext}'
        import os
        from django.conf import settings
        path = Path(settings.MEDIA_ROOT) / fname
        with open(path, 'wb+') as dest:
            for chunk in f.chunks():
                dest.write(chunk)
        Product.objects.filter(id=pid).update(image=f'/static/uploads/{fname}')
    return redirect('/admin/dashboard/')

@csrf_exempt
@login_required
def admin_category_add(request):
    if request.method == 'POST':
        Category.objects.create(name=request.POST.get('name',''))
    return redirect('/admin/dashboard/')

@csrf_exempt
@login_required
def admin_category_edit(request, cid):
    if request.method == 'POST':
        Category.objects.filter(id=cid).update(name=request.POST.get('name',''))
    return redirect('/admin/dashboard/')

@csrf_exempt
@login_required
def admin_category_delete(request, cid):
    Category.objects.filter(id=cid).delete()
    return redirect('/admin/dashboard/')

@csrf_exempt
@login_required
def admin_category_image(request, cid):
    if request.method == 'POST' and request.FILES.get('file'):
        from pathlib import Path
        f = request.FILES['file']
        ext = Path(f.name).suffix or '.jpg'
        fname = f'category_{cid}{ext}'
        from django.conf import settings
        path = Path(settings.MEDIA_ROOT) / fname
        with open(path, 'wb+') as dest:
            for chunk in f.chunks():
                dest.write(chunk)
        Category.objects.filter(id=cid).update(image=f'/static/uploads/{fname}')
    return redirect('/admin/dashboard/')

@login_required
def admin_category_manage_products(request, cid):
    if request.method == 'POST':
        assigned_ids = [int(x) for x in request.POST.getlist('product_ids') if x.isdigit()]
        Product.objects.filter(category_id=cid).update(category=None)
        Product.objects.filter(id__in=assigned_ids).update(category_id=cid)
    return redirect('/admin/dashboard/')

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_category_products(request, cid):
    cat = get_object_or_404(Category, id=cid)
    all_products = Product.objects.filter(active=True)
    assigned_ids = list(all_products.filter(category_id=cid).values_list('id', flat=True))
    return Response({
        'category': cat.name,
        'all_products': ProductSerializer(all_products, many=True).data,
        'assigned_ids': assigned_ids,
    })

@csrf_exempt
@login_required
def admin_testimonial_add(request):
    if request.method == 'POST':
        Testimonial.objects.create(
            name=request.POST.get('name',''),
            city=request.POST.get('city',''),
            text=request.POST.get('text','')
        )
    return redirect('/admin/dashboard/')

@csrf_exempt
@login_required
def admin_testimonial_delete(request, tid):
    Testimonial.objects.filter(id=tid).delete()
    return redirect('/admin/dashboard/')

@csrf_exempt
@login_required
def admin_bundle_edit(request, bid):
    if request.method == 'POST':
        b = get_object_or_404(Bundle, id=bid)
        b.name = request.POST.get('name', b.name)
        b.items = request.POST.get('items', b.items)
        b.price = float(request.POST.get('price', b.price))
        b.old_price = float(request.POST.get('old_price', b.old_price))
        if b.old_price > b.price:
            b.save_percent = round((1 - b.price/b.old_price) * 100)
        b.save()
    return redirect('/admin/dashboard/')

@login_required
def admin_bundle_manage_products(request, bid):
    if request.method == 'POST':
        assigned_ids = [int(x) for x in request.POST.getlist('product_ids') if x.isdigit()]
        names = list(Product.objects.filter(id__in=assigned_ids).values_list('name', flat=True))
        Bundle.objects.filter(id=bid).update(items=', '.join(names))
    return redirect('/admin/dashboard/')

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_bundle_products(request, bid):
    bundle = get_object_or_404(Bundle, id=bid)
    all_products = Product.objects.filter(active=True)
    assigned_names = [n.strip() for n in bundle.items.split(',')] if bundle.items else []
    assigned_ids = list(all_products.filter(name__in=assigned_names).values_list('id', flat=True))
    return Response({
        'bundle': bundle.name,
        'all_products': ProductSerializer(all_products, many=True).data,
        'assigned_ids': assigned_ids,
    })

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_bundle_add_to_cart(request, bid):
    bundle = get_object_or_404(Bundle, id=bid)
    assigned_names = [n.strip() for n in bundle.items.split(',')] if bundle.items else []
    products = Product.objects.filter(active=True, name__in=assigned_names)
    return Response({
        'bundle_name': bundle.name,
        'bundle_price': bundle.price,
        'products': ProductSerializer(products, many=True).data,
    })

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_bundle_detail(request, bid):
    bundle = get_object_or_404(Bundle, id=bid)
    return Response(BundleSerializer(bundle).data)

@csrf_exempt
@login_required
def admin_bundle_add(request):
    if request.method == 'POST':
        name = request.POST.get('name','')
        items = request.POST.get('items','')
        price = float(request.POST.get('price',0))
        old_price = float(request.POST.get('old_price',0))
        save = round((1 - price/old_price) * 100) if old_price > price else 0
        Bundle.objects.create(name=name, items=items, price=price, old_price=old_price, save_percent=save)
    return redirect('/admin/dashboard/')

@csrf_exempt
@login_required
def admin_bundle_delete(request, bid):
    Bundle.objects.filter(id=bid).delete()
    return redirect('/admin/dashboard/')

@csrf_exempt
@login_required
def admin_blog_add(request):
    if request.method == 'POST':
        BlogPost.objects.create(
            slug=slugify(request.POST.get('title','')),
            title=request.POST.get('title',''),
            category=request.POST.get('category','General'),
            read_time=request.POST.get('read_time','5 min'),
            excerpt=request.POST.get('excerpt',''),
            content=request.POST.get('content',''),
        )
    return redirect('/admin/dashboard/')

@csrf_exempt
@login_required
def admin_blog_delete(request, bid):
    BlogPost.objects.filter(id=bid).delete()
    return redirect('/admin/dashboard/')

@csrf_exempt
@login_required
def admin_blog_image(request, bid):
    if request.method == 'POST' and request.FILES.get('file'):
        from pathlib import Path
        f = request.FILES['file']
        ext = Path(f.name).suffix or '.jpg'
        fname = f'blog_{bid}{ext}'
        from django.conf import settings
        path = Path(settings.MEDIA_ROOT) / fname
        with open(path, 'wb+') as dest:
            for chunk in f.chunks():
                dest.write(chunk)
        BlogPost.objects.filter(id=bid).update(image=f'/static/uploads/{fname}')
    return redirect('/admin/dashboard/')

@csrf_exempt
@login_required
def admin_bundle_image(request, bid):
    if request.method == 'POST' and request.FILES.get('file'):
        from pathlib import Path
        f = request.FILES['file']
        ext = Path(f.name).suffix or '.jpg'
        fname = f'bundle_{bid}{ext}'
        from django.conf import settings
        path = Path(settings.MEDIA_ROOT) / fname
        with open(path, 'wb+') as dest:
            for chunk in f.chunks():
                dest.write(chunk)
        Bundle.objects.filter(id=bid).update(image=f'/static/uploads/{fname}')
    return redirect('/admin/dashboard/')

@csrf_exempt
@login_required
def admin_why_edit(request, wid):
    if request.method == 'POST':
        WhyItem.objects.filter(id=wid).update(
            title=request.POST.get('title',''),
            description=request.POST.get('description','')
        )
    return redirect('/admin/dashboard/')

@csrf_exempt
@login_required
def admin_settings_save(request):
    if request.method == 'POST':
        keys = ['site_name','site_tagline','hero_title','hero_subtitle','hero_badge','about_title','about_content','phone','email','address','whatsapp','story_location']
        for k in keys:
            v = request.POST.get(k, '')
            Setting.objects.update_or_create(key=k, defaults={'value': v})
        new_pass = request.POST.get('new_password','')
        if new_pass:
            from django.contrib.auth.models import User
            u = User.objects.first()
            if u:
                u.set_password(new_pass)
                u.save()
    return redirect('/admin/dashboard/')

@csrf_exempt
@login_required
def admin_change_password(request):
    if request.method == 'POST':
        u = request.user
        old = request.POST.get('old_password','')
        new = request.POST.get('new_password','')
        if u.check_password(old) and len(new) >= 4:
            u.set_password(new)
            u.save()
    return redirect('/admin/dashboard/')

@csrf_exempt
@login_required
def admin_message_delete(request, mid):
    ContactMessage.objects.filter(id=mid).delete()
    return redirect('/admin/dashboard/')

@csrf_exempt
@login_required
def admin_upload_image(request):
    if request.method == 'POST' and request.FILES.get('file'):
        f = request.FILES['file']
        target = request.POST.get('target','uploads')
        from pathlib import Path
        from django.conf import settings
        dest = Path(settings.MEDIA_ROOT) / f.name
        with open(dest, 'wb+') as out:
            for chunk in f.chunks():
                out.write(chunk)
        if target == 'hero':
            Setting.objects.update_or_create(key='hero_image', defaults={'value': f'/static/uploads/{f.name}'})
        elif target == 'story':
            Setting.objects.update_or_create(key='story_image', defaults={'value': f'/static/uploads/{f.name}'})
    return redirect('/admin/dashboard/')

# ===== REST API =====
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(active=True)
    serializer_class = ProductSerializer
    lookup_field = 'id'

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class BundleViewSet(viewsets.ModelViewSet):
    queryset = Bundle.objects.all()
    serializer_class = BundleSerializer

class TestimonialViewSet(viewsets.ModelViewSet):
    queryset = Testimonial.objects.filter(active=True)
    serializer_class = TestimonialSerializer

class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.filter(active=True)
    serializer_class = BlogPostSerializer

class WhyItemViewSet(viewsets.ModelViewSet):
    queryset = WhyItem.objects.all()
    serializer_class = WhyItemSerializer

class SettingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Setting.objects.all()
    serializer_class = SettingSerializer

class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_product_detail(request, pid):
    product = get_object_or_404(Product, id=pid, active=True)
    return Response(ProductSerializer(product).data)
