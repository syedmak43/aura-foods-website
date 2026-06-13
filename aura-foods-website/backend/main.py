import os, json, secrets, hmac
from pathlib import Path
from fastapi import FastAPI, Request, Form, UploadFile, File, Cookie, HTTPException, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import init_db, get_setting, set_setting, get_all, get_by_id, delete_by_id
from database import get_products, get_product, get_products_by_category, get_categories
from database import get_testimonials, get_bundles, get_blog_posts, get_blog_post, get_why_items

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

init_db()

UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

@app.on_event("startup")
def startup():
    init_db()

# ===== HELPERS =====
def seo_meta(title, description, url, image=None):
    return {"title": title, "description": description, "url": url, "image": image or "/static/images/hero-spices.jpg"}

def slugify(text):
    return text.lower().replace(" ", "-").replace("--", "-").strip("-")

def check_admin(session_token=None):
    token = get_setting("admin_token", "")
    return token and session_token and hmac.compare_digest(token, session_token)

# ===== PUBLIC ROUTES =====
@app.get("/robots.txt", response_class=HTMLResponse)
async def robots():
    return HTMLResponse(content="""User-agent: *
Allow: /
Disallow: /admin
Sitemap: https://aurafoods.pk/sitemap.xml
""", media_type="text/plain")

@app.get("/sitemap.xml", response_class=HTMLResponse)
async def sitemap():
    urls = [{"loc": "https://aurafoods.pk/", "p": "1.0"}, {"loc": "https://aurafoods.pk/shop", "p": "0.9"}, {"loc": "https://aurafoods.pk/about", "p": "0.7"}, {"loc": "https://aurafoods.pk/blog", "p": "0.8"}, {"loc": "https://aurafoods.pk/contact", "p": "0.6"}]
    for p in get_products():
        urls.append({"loc": f"https://aurafoods.pk/product/{p['slug']}", "p": "0.8"})
    for b in get_blog_posts():
        urls.append({"loc": f"https://aurafoods.pk/blog/{b['slug']}", "p": "0.7"})
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        xml += f"  <url>\n    <loc>{u['loc']}</loc>\n    <priority>{u['p']}</priority>\n  </url>\n"
    return HTMLResponse(content=xml + "</urlset>", media_type="application/xml")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    meta = seo_meta(f"{get_setting('site_name')} — {get_setting('site_tagline')}", get_setting("hero_subtitle"), "https://aurafoods.pk/")
    return templates.TemplateResponse("index.html", {
        "request": request, "meta": meta,
        "products": get_products(), "categories": get_categories(),
        "testimonials": get_testimonials(), "bundles": get_bundles(),
        "why_items": get_why_items(), "blog_posts": get_blog_posts()[:3],
        "settings": {k: get_setting(k) for k in ["site_name","site_tagline","hero_title","hero_subtitle","hero_badge","hero_image","story_image","story_location","phone","email","whatsapp"]},
        "schema_org": json.dumps({"@context":"https://schema.org","@type":"Organization","name":get_setting("site_name"),"url":"https://aurafoods.pk","description":get_setting("site_tagline"),"areaServed":"Pakistan"})
    })

@app.get("/shop", response_class=HTMLResponse)
async def shop(request: Request, category: str = None):
    products = get_products_by_category(category) if category else get_products()
    meta = seo_meta("Shop Organic Spices — Aura Foods Pakistan", "Browse our complete range of pure, organic Pakistani spices.", "https://aurafoods.pk/shop")
    return templates.TemplateResponse("shop.html", {"request": request, "meta": meta, "products": products, "categories": get_categories(), "active_category": category})

@app.get("/product/{slug}", response_class=HTMLResponse)
async def product_detail(request: Request, slug: str):
    product = get_product(slug)
    if not product:
        return templates.TemplateResponse("404.html", {"request": request, "meta": seo_meta("Not Found","","")}, status_code=404)
    related = [p for p in get_products() if p["category_id"] == product["category_id"] and p["id"] != product["id"]][:4]
    meta = seo_meta(f"Buy {product['name']} Online — Aura Foods", product["tagline"], f"https://aurafoods.pk/product/{slug}", product["image"])
    return templates.TemplateResponse("product.html", {"request": request, "meta": meta, "product": product, "related": related})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    meta = seo_meta("About Aura Foods", "Learn about Aura Foods' mission to bring pure, organic Pakistani spices from Sindh farms to your kitchen.", "https://aurafoods.pk/about")
    return templates.TemplateResponse("about.html", {"request": request, "meta": meta, "why_items": get_why_items(), "settings": {k: get_setting(k) for k in ["about_title","about_content","story_image","story_location"]}})

@app.get("/blog", response_class=HTMLResponse)
async def blog(request: Request):
    meta = seo_meta("Aura Foods Blog", "Read about cooking tips, health benefits of spices, and Pakistani food heritage.", "https://aurafoods.pk/blog")
    return templates.TemplateResponse("blog.html", {"request": request, "meta": meta, "blog_posts": get_blog_posts()})

@app.get("/blog/{slug}", response_class=HTMLResponse)
async def blog_detail(request: Request, slug: str):
    post = get_blog_post(slug)
    if not post:
        return templates.TemplateResponse("404.html", {"request": request, "meta": seo_meta("Not Found","","")}, status_code=404)
    other = [b for b in get_blog_posts() if b["slug"] != slug]
    meta = seo_meta(f"{post['title']} — Aura Foods Blog", post["excerpt"], f"https://aurafoods.pk/blog/{slug}", post["image"])
    return templates.TemplateResponse("blog_detail.html", {"request": request, "meta": meta, "post": post, "other_posts": other})

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    meta = seo_meta("Contact Aura Foods", "Reach out for orders, wholesale inquiries, or any questions.", "https://aurafoods.pk/contact")
    return templates.TemplateResponse("contact.html", {"request": request, "meta": meta, "settings": {k: get_setting(k) for k in ["phone","email","address","whatsapp"]}})

@app.get("/cart", response_class=HTMLResponse)
async def cart(request: Request):
    return templates.TemplateResponse("cart.html", {"request": request, "meta": seo_meta("Cart — Aura Foods","","https://aurafoods.pk/cart")})

@app.get("/checkout", response_class=HTMLResponse)
async def checkout(request: Request):
    return templates.TemplateResponse("checkout.html", {"request": request, "meta": seo_meta("Checkout — Aura Foods","","https://aurafoods.pk/checkout")})

@app.get("/order-confirmation", response_class=HTMLResponse)
async def order_confirmation(request: Request):
    return templates.TemplateResponse("order_confirmation.html", {"request": request, "meta": seo_meta("Order Confirmed — Aura Foods","","https://aurafoods.pk/order-confirmation")})

# ===== JSON API (for admin modals) =====
@app.get("/api/product/{pid}")
async def api_product(pid: int):
    from database import get_db
    conn = get_db()
    row = conn.execute("""SELECT p.*, c.name as category_name
        FROM products p LEFT JOIN categories c ON p.category_id=c.id WHERE p.id=?""", (pid,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404)
    return dict(row)

# ===== ADMIN ROUTES =====
@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request})

@app.post("/admin/login")
async def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == get_setting("admin_user") and password == get_setting("admin_pass"):
        token = secrets.token_hex(32)
        set_setting("admin_token", token)
        resp = RedirectResponse(url="/admin", status_code=303)
        resp.set_cookie(key="session", value=token, httponly=True, max_age=86400*7)
        return resp
    return templates.TemplateResponse("admin/login.html", {"request": request, "error": "Invalid credentials"})

@app.get("/admin/logout")
async def admin_logout():
    set_setting("admin_token", "")
    resp = RedirectResponse(url="/admin/login", status_code=303)
    resp.delete_cookie("session")
    return resp

def admin_required(handler):
    async def wrapper(request: Request, *args, **kwargs):
        session = request.cookies.get("session")
        if not check_admin(session):
            return RedirectResponse(url="/admin/login", status_code=303)
        return await handler(request, *args, **kwargs)
    return wrapper

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    session = request.cookies.get("session")
    if not check_admin(session):
        return RedirectResponse(url="/admin/login", status_code=303)
    products = get_products()
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "products": products,
        "categories": get_categories(),
        "testimonials": get_testimonials(),
        "bundles": get_bundles(),
        "blog_posts": get_blog_posts(),
        "why_items": get_why_items(),
        "settings": {k: get_setting(k) for k in ["site_name","site_tagline","hero_title","hero_subtitle","hero_badge","about_title","about_content","phone","email","address","whatsapp","story_location","hero_image","story_image"]},
    })

# Product CRUD
@app.post("/admin/product/add")
async def admin_product_add(request: Request, name: str = Form(...), tagline: str = Form(""), price: float = Form(0), old_price: float = Form(0), weight: str = Form("200g"), category_id: int = Form(1), description: str = Form(""), ingredients: str = Form(""), usage: str = Form(""), best_seller: int = Form(0), new_arrival: int = Form(0)):
    from database import get_db
    conn = get_db()
    slug = slugify(name)
    conn.execute("INSERT INTO products (slug,name,tagline,price,old_price,weight,category_id,description,ingredients,usage,best_seller,new_arrival,active) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,1)", (slug,name,tagline,price,old_price,weight,category_id,description,ingredients,usage,best_seller,new_arrival))
    conn.commit(); conn.close()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/product/edit/{pid}")
async def admin_product_edit(request: Request, pid: int, name: str = Form(...), tagline: str = Form(""), price: float = Form(0), old_price: float = Form(0), weight: str = Form("200g"), category_id: int = Form(1), description: str = Form(""), ingredients: str = Form(""), usage: str = Form(""), best_seller: int = Form(0), new_arrival: int = Form(0)):
    from database import get_db
    conn = get_db()
    slug = slugify(name)
    conn.execute("UPDATE products SET slug=?,name=?,tagline=?,price=?,old_price=?,weight=?,category_id=?,description=?,ingredients=?,usage=?,best_seller=?,new_arrival=? WHERE id=?", (slug,name,tagline,price,old_price,weight,category_id,description,ingredients,usage,best_seller,new_arrival,pid))
    conn.commit(); conn.close()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/product/delete/{pid}")
async def admin_product_delete(request: Request, pid: int):
    delete_by_id("products", pid)
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/product/image/{pid}")
async def admin_product_image(request: Request, pid: int, file: UploadFile = File(...)):
    from database import get_db
    ext = Path(file.filename).suffix if file.filename else ".jpg"
    fname = f"product_{pid}{ext}"
    fpath = UPLOAD_DIR / fname
    content = await file.read()
    fpath.write_bytes(content)
    conn = get_db()
    conn.execute("UPDATE products SET image=? WHERE id=?", (f"/static/uploads/{fname}", pid))
    conn.commit(); conn.close()
    return RedirectResponse(url="/admin", status_code=303)

# Category CRUD
@app.post("/admin/category/add")
async def admin_category_add(request: Request, name: str = Form(...)):
    from database import get_db
    conn = get_db()
    conn.execute("INSERT INTO categories (name) VALUES (?)", (name,))
    conn.commit(); conn.close()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/category/edit/{cid}")
async def admin_category_edit(request: Request, cid: int, name: str = Form(...)):
    from database import get_db
    conn = get_db()
    conn.execute("UPDATE categories SET name=? WHERE id=?", (name, cid))
    conn.commit(); conn.close()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/category/delete/{cid}")
async def admin_category_delete(request: Request, cid: int):
    delete_by_id("categories", cid)
    return RedirectResponse(url="/admin", status_code=303)

# Testimonial CRUD
@app.post("/admin/testimonial/add")
async def admin_testimonial_add(request: Request, name: str = Form(...), city: str = Form(""), text: str = Form(...)):
    from database import get_db
    conn = get_db()
    conn.execute("INSERT INTO testimonials (name,city,text,rating,active) VALUES (?,?,?,5,1)", (name,city,text))
    conn.commit(); conn.close()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/testimonial/delete/{tid}")
async def admin_testimonial_delete(request: Request, tid: int):
    delete_by_id("testimonials", tid)
    return RedirectResponse(url="/admin", status_code=303)

# Bundle CRUD
@app.post("/admin/bundle/add")
async def admin_bundle_add(request: Request, name: str = Form(...), items: str = Form(""), price: float = Form(0), old_price: float = Form(0)):
    save = round((1 - price/old_price) * 100) if old_price > price else 0
    from database import get_db
    conn = get_db()
    conn.execute("INSERT INTO bundles (name,items,price,old_price,save_percent) VALUES (?,?,?,?,?)", (name,items,price,old_price,save))
    conn.commit(); conn.close()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/bundle/delete/{bid}")
async def admin_bundle_delete(request: Request, bid: int):
    delete_by_id("bundles", bid)
    return RedirectResponse(url="/admin", status_code=303)

# Blog CRUD
@app.post("/admin/blog/add")
async def admin_blog_add(request: Request, title: str = Form(...), category: str = Form("General"), read_time: str = Form("5 min"), excerpt: str = Form(""), content: str = Form("")):
    from database import get_db
    conn = get_db()
    slug = slugify(title)
    conn.execute("INSERT INTO blog_posts (slug,title,category,read_time,excerpt,content,active) VALUES (?,?,?,?,?,?,1)", (slug,title,category,read_time,excerpt,content))
    conn.commit(); conn.close()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/blog/delete/{bid}")
async def admin_blog_delete(request: Request, bid: int):
    delete_by_id("blog_posts", bid)
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/blog/image/{bid}")
async def admin_blog_image(request: Request, bid: int, file: UploadFile = File(...)):
    ext = Path(file.filename).suffix if file.filename else ".jpg"
    fname = f"blog_{bid}{ext}"
    fpath = UPLOAD_DIR / fname
    content = await file.read()
    fpath.write_bytes(content)
    from database import get_db
    conn = get_db()
    conn.execute("UPDATE blog_posts SET image=? WHERE id=?", (f"/static/uploads/{fname}", bid))
    conn.commit(); conn.close()
    return RedirectResponse(url="/admin", status_code=303)

# Settings update
@app.post("/admin/settings")
async def admin_settings(request: Request):
    form = await request.form()
    from database import get_db
    conn = get_db()
    for key, val in form.items():
        if key.startswith("setting_"):
            conn.execute("INSERT OR REPLACE INTO settings (key,value) VALUES (?,?)", (key.replace("setting_",""), val))
    conn.commit(); conn.close()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/hero-image")
async def admin_hero_image(request: Request, file: UploadFile = File(...)):
    ext = Path(file.filename).suffix if file.filename else ".jpg"
    fpath = UPLOAD_DIR / f"hero{ext}"
    content = await file.read()
    fpath.write_bytes(content)
    set_setting("hero_image", f"/static/uploads/hero{ext}")
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/story-image")
async def admin_story_image(request: Request, file: UploadFile = File(...)):
    ext = Path(file.filename).suffix if file.filename else ".jpg"
    fpath = UPLOAD_DIR / f"story{ext}"
    content = await file.read()
    fpath.write_bytes(content)
    set_setting("story_image", f"/static/uploads/story{ext}")
    return RedirectResponse(url="/admin", status_code=303)

# Why items
@app.post("/admin/why/edit/{wid}")
async def admin_why_edit(request: Request, wid: int, title: str = Form(...), description: str = Form(...)):
    from database import get_db
    conn = get_db()
    conn.execute("UPDATE why_items SET title=?,description=? WHERE id=?", (title,description,wid))
    conn.commit(); conn.close()
    return RedirectResponse(url="/admin", status_code=303)

# Password change
@app.post("/admin/change-password")
async def admin_change_password(request: Request, current: str = Form(...), newpass: str = Form(...)):
    if current == get_setting("admin_pass"):
        set_setting("admin_pass", newpass)
    return RedirectResponse(url="/admin", status_code=303)

# Upload image (generic)
@app.post("/admin/upload")
async def admin_upload(request: Request, file: UploadFile = File(...)):
    fname = file.filename or "image.jpg"
    fpath = UPLOAD_DIR / fname
    content = await file.read()
    fpath.write_bytes(content)
    return RedirectResponse(url="/admin", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
