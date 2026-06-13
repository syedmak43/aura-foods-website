import sqlite3, os, json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent / "data" / "aurafoods.db"

def get_db():
    os.makedirs(str(DB_PATH.parent), exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            image TEXT DEFAULT '',
            sort_order INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            tagline TEXT DEFAULT '',
            price REAL NOT NULL DEFAULT 0,
            old_price REAL DEFAULT 0,
            weight TEXT DEFAULT '200g',
            image TEXT DEFAULT '',
            category_id INTEGER REFERENCES categories(id),
            description TEXT DEFAULT '',
            ingredients TEXT DEFAULT '',
            usage TEXT DEFAULT '',
            best_seller INTEGER DEFAULT 0,
            new_arrival INTEGER DEFAULT 0,
            featured INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS bundles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            items TEXT DEFAULT '',
            price REAL NOT NULL DEFAULT 0,
            old_price REAL DEFAULT 0,
            save_percent INTEGER DEFAULT 0,
            image TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS testimonials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT DEFAULT '',
            text TEXT NOT NULL,
            rating INTEGER DEFAULT 5,
            active INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS blog_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            read_time TEXT DEFAULT '5 min',
            excerpt TEXT DEFAULT '',
            content TEXT DEFAULT '',
            image TEXT DEFAULT '',
            date TEXT DEFAULT (date('now')),
            active INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS why_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            icon TEXT DEFAULT 'leaf',
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            sort_order INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS site_pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page TEXT UNIQUE NOT NULL,
            title TEXT DEFAULT '',
            subtitle TEXT DEFAULT '',
            content TEXT DEFAULT ''
        );
    """)
    conn.commit()

    # Seed default data if empty
    if not conn.execute("SELECT COUNT(*) FROM settings").fetchone()[0]:
        conn.execute("INSERT OR IGNORE INTO settings VALUES ('site_name','Aura Foods')")
        conn.execute("INSERT OR IGNORE INTO settings VALUES ('site_tagline','Pure & Premium Organic Spices of Pakistan')")
        conn.execute("INSERT OR IGNORE INTO settings VALUES ('hero_title','Pure & Premium <em>Organic Spices</em>')")
        conn.execute("INSERT OR IGNORE INTO settings VALUES ('hero_subtitle','Freshly packed authentic spices from the fields of Sindh, delivered across Pakistan.')")
        conn.execute("INSERT OR IGNORE INTO settings VALUES ('hero_badge','Hand-sourced · Stone-ground · Freshly packed')")
        conn.execute("INSERT OR IGNORE INTO settings VALUES ('about_title','From Sindh Soil to Your Spice Rack')")
        conn.execute("INSERT OR IGNORE INTO settings VALUES ('about_content','We trace every spice back to the family farms of Kunri — the chili capital of Asia.')")
        conn.execute("INSERT OR IGNORE INTO settings VALUES ('phone','+92 300 1234567')")
        conn.execute("INSERT OR IGNORE INTO settings VALUES ('email','hello@aurafoods.pk')")
        conn.execute("INSERT OR IGNORE INTO settings VALUES ('address','Karachi, Sindh, Pakistan')")
        conn.execute("INSERT OR IGNORE INTO settings VALUES ('whatsapp','923001234567')")
        conn.execute("INSERT OR IGNORE INTO settings VALUES ('admin_user','admin')")
        conn.execute("INSERT OR IGNORE INTO settings VALUES ('admin_pass','aura2026')")
        conn.execute("INSERT OR IGNORE INTO settings VALUES ('hero_image','/static/images/hero-spices.jpg')")
        conn.execute("INSERT OR IGNORE INTO settings VALUES ('story_image','/static/images/quality-story.jpg')")
        conn.execute("INSERT OR IGNORE INTO settings VALUES ('story_location','Kunri, Sindh')")
        conn.commit()

    # Seed categories
    if not conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]:
        cats = ["Red Chili Powder","Turmeric Powder","Coriander Powder","Garam Masala","Premium Blends","Salt Range"]
        for i, c in enumerate(cats):
            conn.execute("INSERT INTO categories (name, image, sort_order) VALUES (?,?,?)",
                         (c, f"/static/images/{c.lower().replace(' ','-')}.jpg", i))
        conn.commit()

    # Seed products
    if not conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]:
        cat_map = {r["name"]: r["id"] for r in conn.execute("SELECT * FROM categories").fetchall()}
        prods = [
            ("kunri-red-chili","Kunri Red Chili Powder (Pisi Lal Mirch)","Hand-picked from Sindh",199,249,"200g","/static/uploads/product01.jpeg","Red Chili Powder","Pure red chili powder sourced from Kunri, Sindh — the chili capital of Asia. Vibrant red color, rich aroma, and authentic heat. Stone-ground to preserve essential oils. No additives, no preservatives, no artificial colors.","100% Pure Red Chili (Capsicum annuum)","Ideal for curries, BBQ marinades, and everyday cooking. Add 1 tsp per serving for perfect heat. Store in a cool, dry place.",1,0,1),
            ("golden-turmeric","Golden Turmeric Powder (Pisi Haldi)","Stone-ground pure turmeric",180,220,"200g","/static/uploads/product02.jpeg","Turmeric Powder","High-curcumin turmeric powder stone-ground from premium Pakistani roots. Golden-yellow color with earthy aroma. Sourced from family farms in Sindh. Naturally anti-inflammatory and packed with antioxidants.","100% Pure Turmeric Root (Curcuma longa)","Use in curries, milk (haldi doodh), and wellness drinks. Add 1/2 tsp daily for health benefits. Pairs well with black pepper for better absorption.",1,0,1),
            ("fresh-coriander","Fresh Coriander Powder (Pisa Dhaniya)","Aromatic & finely milled",160,190,"200g","/static/uploads/product03.jpeg","Coriander Powder","Finely ground coriander powder from select Pakistani farms. Citrusy aroma with mild, warming flavor. Essential for authentic Pakistani and Indian cooking. Freshly ground in small batches.","100% Pure Coriander Seeds (Coriandrum sativum)","Essential for dals, curries, and spice blends. Toast lightly in a dry pan before use for enhanced flavor. Add 1 tsp per serving.",0,1,1),
            ("black-pepper-powder","Black Pepper Powder (Pisi Kali Mirch)","Freshly ground, bold & pungent",190,230,"100g","/static/uploads/product04.jpeg","Premium Blends","Premium black pepper powder from carefully selected peppercorns. Bold, pungent aroma with a sharp kick. Perfect for everyday seasoning and finishing dishes. No fillers or additives.","100% Pure Black Pepper (Piper nigrum)","Use as a table spice or in cooking. Add 1/4 tsp per serving. Grind fresh for best results. Essential for garam masala and spice blends.",0,1,1),
            ("chaat-masala","Tangy Chaat Masala","Street-style zing",140,170,"100g","/static/uploads/product05.jpeg","Premium Blends","Zesty, tangy masala that brings authentic street food flavor to your home. Perfect for fruits, salads, yogurt, and snacks. Our signature blend combines mango powder, black salt, and aromatic spices.","Cumin, Coriander, Mango Powder (Amchur), Black Salt (Kala Namak), Red Chili, Ginger, Mint, Black Pepper, Citric Acid","Sprinkle on fruit chaat, salads, yogurt, or use as a finishing spice for any snack. Also great on grilled corn and roasted nuts.",1,0,1),
            ("pink-salt","Himalayan Pink Salt (Gulabi Namak)","Pure, mineral-rich rock salt",120,150,"200g","/static/uploads/product06.jpeg","Salt Range","Premium Himalayan pink salt mined from the Khewra Salt Mine — the second largest salt mine in the world. Rich in trace minerals including potassium, magnesium, and calcium. Chemical-free and unrefined.","100% Natural Himalayan Pink Salt","Use as a finishing salt, in cooking, or in salt grinders. Also great for salt therapy and bath soaks. Replace regular table salt for a healthier alternative.",0,0,1),
            ("rock-salt","Rock Salt (Kala Namak)","Authentic sulfurous mineral salt",110,140,"200g","/static/uploads/product07.jpeg","Salt Range","Traditional black mineral salt with characteristic sulfurous aroma. Essential for authentic South Asian cuisine. Mined from natural deposits in Pakistan. A staple in chaat, raita, and chutneys.","100% Natural Black Mineral Salt","Crush before use. Essential for chaat masala, fruit salads, raita, and chutneys. Adds an egg-like flavor to vegan dishes. Use sparingly — 1/4 tsp is enough.",0,0,1),
            ("royal-garam-masala","Royal Garam Masala","Heritage 14-spice blend",250,300,"100g","/static/uploads/product08.jpeg","Garam Masala","Our signature blend of 14 hand-roasted and stone-ground spices. Cardamom, cinnamon, cloves, cumin, nutmeg, and more. Each batch is slow-roasted to unlock deep, complex flavors. No preservatives or artificial colors.","Cardamom (Green + Black), Cinnamon, Cloves, Cumin, Nutmeg, Mace, Black Pepper, Bay Leaf, Star Anise, Fennel, Coriander, Ginger, White Pepper","Add at the end of cooking for maximum aroma. Perfect for biryani, curries, korma, and lentil dishes. Use 1 tsp per kg of meat. Toast gently before adding for deeper flavor.",1,0,1),
        ]
        for p in prods:
            slug, name, tagline, price, old, w, img, cat, desc, ing, use, bs, na, feat = p
            cid = cat_map.get(cat, 1)
            conn.execute("""INSERT INTO products (slug,name,tagline,price,old_price,weight,image,category_id,description,ingredients,usage,best_seller,new_arrival,featured,active) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,1)""",
                         (slug,name,tagline,price,old,w,img,cid,desc,ing,use,bs,na,feat))
        conn.commit()

    # Seed testimomials
    if not conn.execute("SELECT COUNT(*) FROM testimonials").fetchone()[0]:
        tests = [
            ("Ayesha K.","Karachi","The Kunri chili is unreal — the colour, the aroma, exactly what my mother used to buy from the village.",5),
            ("Bilal R.","Lahore","Switched my whole pantry to Aura. The garam masala makes a difference you can smell from the next room.",5),
            ("Sana M.","Islamabad","Beautifully packed, super fresh, and delivered in two days. The biryani masala is restaurant-grade.",5),
            ("Tariq A.","Rawalpindi","Ordered the BBQ bundle for a family gathering. Everyone asked where I got the spices!",5),
            ("Fatima Z.","Faisalabad","Finally, organic spices I can trust. My children's food is now completely preservative-free.",5),
        ]
        for t in tests:
            conn.execute("INSERT INTO testimonials (name,city,text,rating) VALUES (?,?,?,?)", t)
        conn.commit()

    # Seed blog posts
    if not conn.execute("SELECT COUNT(*) FROM blog_posts").fetchone()[0]:
        posts = [
            ("health-benefits-turmeric","The Health Benefits of Daily Turmeric","Wellness","4 min","Discover why golden turmeric is called the king of spices and how daily consumption can transform your health.","<p>Aura Foods is committed to bringing you the finest organic spices from Pakistan.</p><p>We believe that great food starts with great ingredients. That's why every spice we offer is carefully selected, hand-sorted, and stone-ground to preserve its natural essence.</p><h2>Why Quality Matters</h2><p>When you choose Aura Foods, you choose purity. No preservatives. No artificial colors. Just the authentic taste of Pakistan's finest spices, delivered fresh to your doorstep.</p>","/static/images/turmeric.jpg","2026-05-15"),
            ("perfect-bbq-spices","Best Spices for the Perfect BBQ Night","Cooking","6 min","Elevate your barbecue game with these essential spice blends and marinade techniques.","<p>The secret to an unforgettable BBQ lies in the spices. Our Smoky BBQ Rub is crafted with smoked paprika, cumin, and a secret blend of herbs that will transform your grilling.</p><h2>Tips for Perfect BBQ</h2><p>1. Apply rub 30 minutes before grilling<br>2. Let meat rest after applying rub<br>3. Use high heat for searing, then low for cooking</p>","/static/images/bbq.jpg","2026-05-10"),
            ("sindh-spice-heritage","Inside Sindh: Pakistan's Spice Heritage","Heritage","5 min","Journey through the spice farms of Sindh and learn about Pakistan's rich culinary traditions.","<p>Sindh has been a spice-growing region for centuries. The fertile soil, combined with traditional farming methods passed down through generations, produces some of the world's most flavorful spices.</p><h2>The Kunri Region</h2><p>Known as the chili capital of Asia, Kunri in Sindh produces chilies prized for their vibrant color and rich aroma.</p>","/static/images/garam.jpg","2026-05-05"),
        ]
        for p in posts:
            conn.execute("INSERT INTO blog_posts (slug,title,category,read_time,excerpt,content,image,date) VALUES (?,?,?,?,?,?,?,?)", p)
        conn.commit()

    # Seed bundles
    if not conn.execute("SELECT COUNT(*) FROM bundles").fetchone()[0]:
        bundles = [
            ("BBQ Master Bundle","Smoky BBQ Rub + Chaat Masala + Red Chili",490,620,21),
            ("Kitchen Essentials","Red Chili + Turmeric + Coriander Powder",430,540,20),
            ("Biryani Night Pack","Biryani Masala + Garam Masala + Turmeric",560,690,19),
        ]
        for b in bundles:
            conn.execute("INSERT INTO bundles (name,items,price,old_price,save_percent) VALUES (?,?,?,?,?)", b)
        conn.commit()

    # Seed site pages
    if not conn.execute("SELECT COUNT(*) FROM site_pages").fetchone()[0]:
        conn.execute("INSERT INTO site_pages (page,title,subtitle) VALUES ('about','Our Story','From the sun-drenched fields of Sindh to your kitchen — Aura Foods is on a mission to bring back the authentic taste of Pakistani spices.')")
        conn.commit()

    # Seed why items
    if not conn.execute("SELECT COUNT(*) FROM why_items").fetchone()[0]:
        why = [
            ("leaf","100% Organic","Sourced from trusted Pakistani farms without synthetic chemicals.",0),
            ("shield","No Preservatives","Nothing artificial added. Ever. Just pure spice.",1),
            ("sparkles","No Artificial Colors","Pure pigment comes from the spice itself, not chemicals.",2),
            ("award","Hygienically Packed","Sealed in food-grade facilities with strict quality control.",3),
            ("truck","Fast Delivery","Across Pakistan in 2-4 business days. Track your order.",4),
            ("flame","Fresh Aroma","Ground in small batches weekly to preserve essential oils.",5),
        ]
        for w in why:
            conn.execute("INSERT INTO why_items (icon,title,description,sort_order) VALUES (?,?,?,?)", w)
        conn.commit()

    conn.close()
    print("Database initialized successfully.")

# ===== CRUD HELPERS =====

def get_all(table):
    conn = get_db()
    rows = conn.execute(f"SELECT * FROM {table} ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_by_id(table, id):
    conn = get_db()
    row = conn.execute(f"SELECT * FROM {table} WHERE id=?", (id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def delete_by_id(table, id):
    conn = get_db()
    conn.execute(f"DELETE FROM {table} WHERE id=?", (id,))
    conn.commit()
    conn.close()

def get_setting(key, default=""):
    conn = get_db()
    r = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return r["value"] if r else default

def set_setting(key, value):
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)", (key, value))
    conn.commit()
    conn.close()

def get_products():
    conn = get_db()
    rows = conn.execute("""SELECT p.*, c.name as category_name
        FROM products p LEFT JOIN categories c ON p.category_id=c.id
        WHERE p.active=1 ORDER BY p.featured DESC, p.id""").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_product(slug):
    conn = get_db()
    row = conn.execute("""SELECT p.*, c.name as category_name
        FROM products p LEFT JOIN categories c ON p.category_id=c.id
        WHERE p.slug=? AND p.active=1""", (slug,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_products_by_category(cat_slug):
    conn = get_db()
    rows = conn.execute("""SELECT p.*, c.name as category_name
        FROM products p LEFT JOIN categories c ON p.category_id=c.id
        WHERE p.active=1 AND LOWER(REPLACE(c.name,' ','-'))=?""", (cat_slug,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_categories():
    conn = get_db()
    rows = conn.execute("SELECT c.*, COUNT(p.id) as count FROM categories c LEFT JOIN products p ON p.category_id=c.id AND p.active=1 GROUP BY c.id ORDER BY c.sort_order").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_testimonials():
    conn = get_db()
    rows = conn.execute("SELECT * FROM testimonials WHERE active=1 ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_bundles():
    conn = get_db()
    rows = conn.execute("SELECT * FROM bundles ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_blog_posts():
    conn = get_db()
    rows = conn.execute("SELECT * FROM blog_posts WHERE active=1 ORDER BY date DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_blog_post(slug):
    conn = get_db()
    row = conn.execute("SELECT * FROM blog_posts WHERE slug=? AND active=1", (slug,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_why_items():
    conn = get_db()
    rows = conn.execute("SELECT * FROM why_items ORDER BY sort_order").fetchall()
    conn.close()
    rows_list = [dict(r) for r in rows]
    SVG_PATHS = {
        "leaf": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
        "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
        "sparkles": '<path d="M12 2l2.4 7.2h7.6l-6 4.8 2.4 7.2-6-4.8-6 4.8 2.4-7.2-6-4.8h7.6z"/>',
        "award": '<circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/>',
        "truck": '<rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/>',
        "flame": '<path d="M8.5 14.5A2.5 2.5 0 0011 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 11-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 002.5 2.5z"/>',
    }
    for item in rows_list:
        item["svg"] = SVG_PATHS.get(item["icon"], "")
    return rows_list

def get_messages():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM contact_messages ORDER BY created_at DESC").fetchall()
    except:
        rows = []
    conn.close()
    return [dict(r) for r in rows]

if __name__ == "__main__":
    init_db()
    print("DB ready.")
