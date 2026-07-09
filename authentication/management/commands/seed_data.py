import io
import urllib.request
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from products.models import Category, Product, ProductImage
from orders.models import Address, Order, OrderItem
from authentication.models import BuyerProfile, SellerProfile

User = get_user_model()


def fetch_image(url, filename):
    """Download image bytes from URL (or read from local path) and return a Django ContentFile."""
    try:
        if url.startswith('/'):
            # Local file path
            with open(url, 'rb') as f:
                data = f.read()
        else:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
        return ContentFile(data, name=filename)
    except Exception as e:
        return None


def seed_product(seller, category, name, details, price, stock, img_url, stdout):
    """Create a Product and attach a ProductImage downloaded from img_url."""
    product = Product.objects.create(
        seller=seller,
        category=category,
        name=name,
        details=details,
        price=price,
        stock=stock,
    )
    safe_name = name.lower().replace(' ', '_').replace('/', '_')[:40]
    img_file = fetch_image(img_url, f"{safe_name}.jpg")
    if img_file:
        ProductImage.objects.create(product=product, image=img_file, is_primary=True, order=0)
    else:
        stdout.write(f"  [warn] Could not fetch image for: {name}")
    return product


class Command(BaseCommand):
    help = "Seeds the database with e-commerce data (sellers, buyers, profiles, addresses, products, orders, items)."

    def handle(self, *args, **options):
        self.stdout.write("Clearing existing data...")
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Address.objects.all().delete()
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        BuyerProfile.objects.all().delete()
        SellerProfile.objects.all().delete()
        User.objects.all().delete()

        # ─────────────────────────────────────────────
        # CATEGORIES
        # ─────────────────────────────────────────────
        self.stdout.write("Seeding categories...")
        electronics = Category.objects.create(name="Electronics")
        fashion     = Category.objects.create(name="Fashion")
        home_living = Category.objects.create(name="Home & Living")
        sports      = Category.objects.create(name="Sports & Fitness")
        beauty      = Category.objects.create(name="Beauty")
        accessories = Category.objects.create(name="Accessories")
        toys        = Category.objects.create(name="Toys & Games")
        books       = Category.objects.create(name="Books")

        # ─────────────────────────────────────────────
        # SELLERS
        # ─────────────────────────────────────────────
        self.stdout.write("Seeding sellers...")

        def make_seller(username, email, store_name, store_desc):
            s = User.objects.create_user(username=username, email=email, password="password123", role="Seller")
            sp = s.seller_profile
            sp.store_name = store_name
            sp.store_description = store_desc
            sp.save()
            return s

        seller1 = make_seller("gadget_hub",       "seller1@example.com", "Gadget Hub Store",   "Your one-stop shop for all things electronic.")
        seller2 = make_seller("chic_wear",         "seller2@example.com", "Chic Wear Boutique", "Trendy fashion and clothing for all seasons.")
        seller3 = make_seller("home_haven",        "seller3@example.com", "Home Haven",         "Beautiful products to make your home cozy and complete.")
        seller4 = make_seller("sport_zone",        "seller4@example.com", "Sport Zone",         "Premium sports and fitness gear for every level.")
        seller5 = make_seller("beauty_bliss",      "seller5@example.com", "Beauty Bliss",       "Curated skincare, makeup and personal care essentials.")
        seller6 = make_seller("accessories_co",    "seller6@example.com", "Accessories Co.",    "Stylish accessories for every occasion.")
        seller7 = make_seller("toy_world",         "seller7@example.com", "Toy World",          "Fun, safe and educational toys for children of all ages.")
        seller8 = make_seller("book_nook",         "seller8@example.com", "Book Nook",          "Handpicked books across genres — fiction, non-fiction, children and more.")

        # ─────────────────────────────────────────────
        # BUYERS
        # ─────────────────────────────────────────────
        self.stdout.write("Seeding buyers...")

        def make_buyer(username, email, phone):
            b = User.objects.create_user(username=username, email=email, password="password123", role="Buyer")
            b.buyer_profile.phone_number = phone
            b.buyer_profile.save()
            return b

        buyer1 = make_buyer("john_doe",    "buyer1@example.com", "+1234567890")
        buyer2 = make_buyer("alice_smith", "buyer2@example.com", "+9876543210")
        buyer3 = make_buyer("bob_jones",   "buyer3@example.com", "+1112223333")
        buyer4 = make_buyer("priya_mehta", "buyer4@example.com", "+9112223344")
        buyer5 = make_buyer("rahul_k",     "buyer5@example.com", "+9223334455")

        # ─────────────────────────────────────────────
        # ADDRESSES
        # ─────────────────────────────────────────────
        self.stdout.write("Seeding addresses...")
        addr1 = Address.objects.create(user=buyer1, address_line1="123 Main St",        address_line2="Apt 4B",    city="New York",    state="NY",          postal_code="10001", country="USA",   is_default=True)
        addr2 = Address.objects.create(user=buyer1, address_line1="456 Work Ave",       address_line2="Suite 300", city="San Francisco",state="CA",         postal_code="94105", country="USA",   is_default=False)
        addr3 = Address.objects.create(user=buyer2, address_line1="789 Pine Rd",                                   city="Seattle",     state="WA",          postal_code="98101", country="USA",   is_default=True)
        addr4 = Address.objects.create(user=buyer2, address_line1="101 Lake Dr",                                   city="Bellevue",    state="WA",          postal_code="98004", country="USA",   is_default=False)
        addr5 = Address.objects.create(user=buyer3, address_line1="202 Elm St",                                    city="Austin",      state="TX",          postal_code="78701", country="USA",   is_default=True)
        addr6 = Address.objects.create(user=buyer4, address_line1="14 MG Road",                                    city="Bengaluru",   state="Karnataka",   postal_code="560001",country="India", is_default=True)
        addr7 = Address.objects.create(user=buyer5, address_line1="7 Connaught Place",                             city="New Delhi",   state="Delhi",       postal_code="110001",country="India", is_default=True)

        # ─────────────────────────────────────────────
        # PRODUCTS
        # ─────────────────────────────────────────────
        p = lambda seller, cat, name, details, price, stock, url: seed_product(
            seller, cat, name, details, price, stock, url, self.stdout
        )

        self.stdout.write("Seeding Electronics products...")
        earbuds      = p(seller1, electronics, "Wireless Earbuds Pro",      "Premium noise-canceling wireless earbuds with 30-hour battery life, IPX5 water resistance, and rich deep bass.",                                               2499, 50, "https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?w=600")
        watch        = p(seller1, electronics, "Smart Fitness Watch",        "Advanced fitness tracking smartwatch with heart rate monitor, SpO2 sensor, GPS, and 7-day battery life.",                                                       8999, 20, "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600")
        keyboard     = p(seller1, electronics, "Mechanical Keyboard",        "Compact RGB backlit mechanical keyboard with tactile blue switches, N-key rollover and detachable USB-C cable.",                                                4999, 15, "https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?w=600")
        headset      = p(seller1, electronics, "Gaming Headset 7.1",         "7.1 surround sound gaming headset with noise-canceling mic, memory foam ear cushions, and 50mm drivers.",                                                      3499, 25, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600")
        webcam       = p(seller1, electronics, "1080p HD Webcam",            "Full HD 1080p webcam with built-in stereo mic, auto light correction, and plug-and-play USB setup.",                                                           2199, 30, "https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=600")
        hub          = p(seller1, electronics, "7-in-1 USB-C Hub",           "Compact USB-C hub with HDMI 4K, 3x USB-A 3.0, SD/MicroSD card reader, 100W PD charging pass-through.",                                                        1899, 40, "https://images.unsplash.com/photo-1625895197185-efcec01cffe0?w=600")
        charger      = p(seller1, electronics, "65W GaN Fast Charger",       "Ultra-compact 65W GaN charger with USB-C PD and USB-A QC 3.0. Charges laptops, phones, and tablets simultaneously.",                                           2799, 60, "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=600")
        laptop_stand = p(seller1, electronics, "Adjustable Laptop Stand",    "Ergonomic aluminium laptop stand with 6 height settings, anti-slip pads, and foldable design for portability.",                                               1599, 35, "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?w=600")
        powerbank    = p(seller1, electronics, "20000mAh Power Bank",        "Ultra-high capacity power bank with dual USB-A, USB-C PD 22.5W fast charging, and LED battery indicator.",                                                    3299, 45, "https://images.unsplash.com/photo-1585338447937-7082f8fc763d?w=600")

        self.stdout.write("Seeding Fashion products...")
        jacket   = p(seller2, fashion, "Classic Denim Jacket",          "Timeless indigo denim jacket with button-front closure, chest pockets, and a comfortable relaxed fit.",                                              2799, 30, "https://images.unsplash.com/photo-1551537482-f2075a1d41f2?w=600")
        boots    = p(seller2, fashion, "Genuine Leather Ankle Boots",   "Handcrafted full-grain leather ankle boots with cushioned insole, rubber outsole, and side zip fastening.",                                          6499, 10, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600")
        tshirt   = p(seller2, fashion, "Organic Cotton T-Shirt",        "Breathable GOTS-certified organic cotton tee with a relaxed unisex fit and reinforced shoulder seams.",                                              799,  100,"https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600")
        sneakers = p(seller2, fashion, "Chunky Platform Sneakers",      "Trendy platform sneakers with premium suede upper, memory foam insole, and chunky rubber outsole.",                                                  3999, 20, "https://images.unsplash.com/photo-1600185365926-3a2ce3cdb9eb?w=600")
        dress    = p(seller2, fashion, "Floral Wrap Midi Dress",        "Elegant floral print wrap dress in flowing rayon. V-neckline, adjustable tie waist, and midi length.",                                              1899, 25, "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=600")
        chinos   = p(seller2, fashion, "Slim-Fit Chino Trousers",       "Smart-casual stretch cotton chinos with slim tapered leg, zip fly, and side pockets. Available in khaki.",                                          1699, 40, "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=600")
        hoodie   = p(seller2, fashion, "Oversized Fleece Hoodie",       "Ultra-soft 320gsm brushed fleece hoodie with kangaroo pocket, adjustable drawstring, and ribbed cuffs.",                                            2199, 35, "https://images.unsplash.com/photo-1565693413579-8ff3fdc1b03b?w=600")
        cap      = p(seller2, fashion, "Classic Baseball Cap",          "Unstructured cotton baseball cap with adjustable snapback, breathable eyelets, and embroidered logo.",                                               599,  80, "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=600")

        self.stdout.write("Seeding Home & Living products...")
        cushions      = p(seller3, home_living, "Velvet Sofa Cushion Set",       "Set of 4 premium velvet throw cushions in blush pink with invisible zip covers and feather-fill insert.",            1499, 40, "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600")
        candle        = p(seller3, home_living, "Luxury Scented Soy Candle",     "Hand-poured soy wax candle with a 60-hour burn time. Jasmine & Sandalwood fragrance.",                               899,  60, "/Users/mahipanara/Desktop/Ecommarce/seed_images/luxury_candle.jpg")
        cutting_board = p(seller3, home_living, "Bamboo Cutting Board Set",      "Set of 3 organic bamboo cutting boards with juice groove and built-in handle. Dishwasher safe.",                     1199, 50, "/Users/mahipanara/Desktop/Ecommarce/seed_images/cutting_board.jpg")
        wall_clock    = p(seller3, home_living, "Minimalist Wall Clock",         "Silent sweep mechanism wall clock with brushed gold frame and clean white face. 30cm diameter.",                      1299, 25, "https://images.unsplash.com/photo-1563861826100-9cb868fdbe1c?w=600")
        desk_lamp     = p(seller3, home_living, "LED Desk Lamp with USB Port",   "Dimmable LED desk lamp with 5 colour temperature modes, USB charging port, and flexible gooseneck arm.",             1799, 30, "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=600")
        diffuser      = p(seller3, home_living, "Aroma Ultrasonic Diffuser",     "400ml ultrasonic essential oil diffuser with 7-colour LED mood lighting and auto-shutoff safety feature.",           1399, 35, "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=600")
        planter       = p(seller3, home_living, "Ceramic Planter Set of 3",      "Set of 3 handcrafted ceramic planters with drainage holes and saucers. Matte white finish. For succulents.",         999,  55, "https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=600")
        mirrors       = p(seller3, home_living, "Gold Arch Wall Mirror",         "Elegant arched wall mirror with a gold-tinted metal frame. 45cm x 120cm. Adds depth to any room.",                  3499, 15, "https://images.unsplash.com/photo-1618220179428-22790b461013?w=600")
        storage       = p(seller3, home_living, "Woven Seagrass Storage Basket", "Handwoven natural seagrass storage basket with dual leather handles. 35cm x 25cm. For blankets or toys.",           1099, 45, "/Users/mahipanara/Desktop/Ecommarce/seed_images/seagrass_basket.jpg")

        self.stdout.write("Seeding Sports & Fitness products...")
        yoga_mat         = p(seller4, sports, "Non-Slip Yoga Mat 6mm",       "6mm thick TPE eco-friendly yoga mat with alignment lines, carrying strap, and superior grip on both sides.",        1299, 60, "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=600")
        resistance_bands = p(seller4, sports, "Resistance Bands Set of 5",   "Set of 5 latex-free resistance bands (10-50lbs), includes door anchor, ankle straps, and carry bag.",             899,  80, "/Users/mahipanara/Desktop/Ecommarce/seed_images/resistance_bands.jpg")
        shaker           = p(seller4, sports, "Protein Shaker Bottle 750ml", "750ml BPA-free Tritan shaker with stainless mesh strainer, leak-proof lid, and measurement markings.",              499,  100,"https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600")
        jump_rope        = p(seller4, sports, "Speed Jump Rope",             "Adjustable bearing speed jump rope with lightweight aluminium handles and PVC cable. Ideal for HIIT training.",    399,  120,"https://images.unsplash.com/photo-1598971861713-54ad16a7e72e?w=600")
        water_bottle     = p(seller4, sports, "Insulated Steel Bottle 500ml","Double-wall vacuum insulated stainless steel bottle. Keeps drinks cold 24h or hot 12h. BPA free.",               799,  90, "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600")
        gym_gloves       = p(seller4, sports, "Weightlifting Gym Gloves",    "Full palm protection gym gloves with wrist wrap, anti-slip silicone grip, and breathable mesh back.",              699,  70, "https://images.unsplash.com/photo-1581009137042-c552e485697a?w=600")
        foam_roller      = p(seller4, sports, "Deep Tissue Foam Roller",     "High-density 45cm foam roller with EVA surface grid for targeted muscle relief and myofascial release.",           1099, 40, "/Users/mahipanara/Desktop/Ecommarce/seed_images/foam_roller.jpg")
        duffel           = p(seller4, sports, "Sports Duffel Bag 40L",       "40L water-resistant polyester duffel with separate shoe compartment, wet pocket, and adjustable shoulder strap.",  1499, 35, "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600")

        self.stdout.write("Seeding Beauty products...")
        serum       = p(seller5, beauty, "Vitamin C Brightening Serum",  "10% stable Vitamin C + E + Ferulic Acid serum for brightening, anti-aging, and fading dark spots.",          1499, 55, "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600")
        moisturizer = p(seller5, beauty, "Hydrating Gel Moisturizer",    "Oil-free lightweight gel moisturizer with hyaluronic acid and niacinamide. Suitable for all skin types.",     899,  70, "/Users/mahipanara/Desktop/Ecommarce/seed_images/moisturizer.jpg")
        sunscreen   = p(seller5, beauty, "SPF 50 Mineral Sunscreen",     "Broad-spectrum SPF 50 PA++++ mineral sunscreen with zinc oxide. No white cast, non-comedogenic, reef-safe.", 699,  80, "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=600")
        lip_set     = p(seller5, beauty, "Satin Lip Colour Set of 6",    "Set of 6 highly-pigmented satin finish lipsticks in curated nudes and berry tones. 8-hour wear formula.",    1299, 45, "/Users/mahipanara/Desktop/Ecommarce/seed_images/lip_colour_set.jpg")
        eye_palette = p(seller5, beauty, "18-Pan Nude Eye Shadow Palette","18-pan neutral eyeshadow palette with matte and shimmer finishes. Blendable, long-lasting pigments.",        1799, 30, "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=600")
        face_mask   = p(seller5, beauty, "Korean Sheet Mask Bundle 10pk","10-pack hydrating sheet masks with hyaluronic acid, collagen, and aloe vera. For all skin types.",           599,  100,"https://images.unsplash.com/photo-1596704017254-9b121068fb31?w=600")
        hair_oil    = p(seller5, beauty, "Moroccan Argan Hair Oil 100ml", "100ml pure Moroccan argan oil blend for frizz control, deep conditioning, and overnight repair treatments.", 849,  65, "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?w=600")
        perfume     = p(seller5, beauty, "Floral Eau de Parfum 50ml",    "A floral bouquet of rose, jasmine and white musk. Long-lasting 50ml EDP. Perfect for daytime wear.",         2499, 25, "https://images.unsplash.com/photo-1594035910387-fea47794261f?w=600")

        self.stdout.write("Seeding Accessories products...")
        wallet      = p(seller6, accessories, "Slim Genuine Leather Wallet",  "Minimalist bifold wallet in full-grain leather with 6 card slots, ID window, and RFID blocking lining.",       1299, 50, "/Users/mahipanara/Desktop/Ecommarce/seed_images/leather_wallet.jpg")
        tote        = p(seller6, accessories, "Heavy Duty Canvas Tote Bag",   "Heavy-duty 12oz canvas tote with zippered inner pocket, reinforced handles, and natural cotton lining.",        899,  70, "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=600")
        scarf       = p(seller6, accessories, "Lightweight Silk Scarf",       "Pure silk twill scarf (90x90cm) with hand-rolled edges and vibrant floral print. A versatile accessory.",       1799, 30, "https://images.unsplash.com/photo-1601924994987-69e26d50dc26?w=600")
        steel_watch = p(seller6, accessories, "Minimalist Steel Watch",       "36mm stainless steel case, sapphire crystal glass, Swiss quartz movement, and genuine leather strap.",          5499, 15, "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=600")
        sunglasses  = p(seller6, accessories, "Polarized Aviator Sunglasses", "UV400 polarized aviator sunglasses with stainless steel frame, spring hinges, and anti-glare coating.",         1499, 40, "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=600")
        belt        = p(seller6, accessories, "Full-Grain Leather Belt",      "35mm full-grain leather belt with solid brass pin buckle. Available in black or brown. Classic cut.",            999,  60, "/Users/mahipanara/Desktop/Ecommarce/seed_images/leather_belt.jpg")
        backpack    = p(seller6, accessories, "Minimalist Backpack 20L",      "20L waterproof nylon backpack with padded laptop sleeve (up to 15in), hidden back pocket, and USB pass-through.",2999, 22, "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600")

        self.stdout.write("Seeding Toys & Games products...")
        lego        = p(seller7, toys, "Creative Builder Block Set 500pcs","500-piece compatible building block set with instruction booklet and storage box. Ages 6+.",                  1599, 30, "https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=600")
        puzzle      = p(seller7, toys, "1000-Piece World Map Jigsaw",      "High-resolution 1000-piece jigsaw puzzle featuring a vibrant world map. Finished size: 70x50cm.",            699,  50, "https://images.unsplash.com/photo-1611996575749-79a3a250f948?w=600")
        playdoh     = p(seller7, toys, "Play Clay Mega Pack 24 Colours",   "24-colour play clay mega pack in resealable tubs. Non-toxic, gluten-free formula. Ages 3+.",                 899,  60, "https://images.unsplash.com/photo-1560343776-97e7d202ff0e?w=600")
        board_game  = p(seller7, toys, "3-in-1 Family Board Game Set",     "3-in-1 family game bundle: Snakes & Ladders, Ludo, and Chess. Foldable board with travel case. Ages 5+.",    1199, 40, "https://images.unsplash.com/photo-1611996575749-79a3a250f948?w=600")
        rc_car      = p(seller7, toys, "Remote Control Off-Road Car 1:18", "1:18 scale 4WD remote control car with 2.4GHz signal, 30km/h speed, and rechargeable battery. Ages 8+.",    2299, 20, "/Users/mahipanara/Desktop/Ecommarce/seed_images/rc_car.jpg")
        clay_kit    = p(seller7, toys, "Air-Dry Modelling Clay Kit",       "Starter kit with 10 colours of air-dry clay, sculpting tools, and project guide. No oven needed. Ages 7+.", 799,  55, "https://images.unsplash.com/photo-1596460107916-430662021049?w=600")
        telescope   = p(seller7, toys, "Kids Starter Telescope 70mm",      "70mm refractor telescope with 2 eyepieces, erecting eyepiece for terrestrial viewing, and adjustable tripod.",3499, 12, "https://images.unsplash.com/photo-1513569771920-c9e1d31714af?w=600")

        self.stdout.write("Seeding Books products...")
        atomic      = p(seller8, books, "Atomic Habits (Paperback)",         "James Clear's bestselling guide to building good habits and breaking bad ones. Over 10 million copies sold.",   499, 80, "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=600")
        sapiens     = p(seller8, books, "Sapiens: A Brief History",          "Yuval Noah Harari's landmark survey of human history — from the Stone Age to the 21st century.",              599, 70, "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=600")
        cook_book   = p(seller8, books, "The Complete Indian Cookbook",      "500+ authentic Indian recipes spanning regional cuisines, street food, desserts and festive specials.",          799, 45, "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=600")
        design_book = p(seller8, books, "Don't Make Me Think (UX Design)",   "Steve Krug's classic web usability guide — essential reading for designers and developers.",                   699, 35, "https://images.unsplash.com/photo-1586717791821-3f44a563fa4c?w=600")
        rich_dad    = p(seller8, books, "Rich Dad Poor Dad",                 "Robert Kiyosaki's personal finance classic on building wealth, investing, and financial independence.",          349, 100,"https://images.unsplash.com/photo-1553729459-efe14ef6055d?w=600")
        children_bk = p(seller8, books, "The Gruffalo - Children's Book",    "Julia Donaldson and Axel Scheffler's beloved illustrated children's book. Ages 2-6. Hardcover edition.",       399, 60, "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=600")
        fiction     = p(seller8, books, "The Midnight Library (Novel)",      "Matt Haig's heartwarming novel about a woman who discovers a library containing books of her unlived lives.",  449, 55, "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600")

        # ─────────────────────────────────────────────
        # ORDERS
        # ─────────────────────────────────────────────
        self.stdout.write("Seeding orders...")

        def make_order(buyer, address, items):
            """items = list of (product, qty) tuples"""
            order = Order.objects.create(buyer=buyer, shipping_address=address, shipping_address_text=str(address), total_price=0.00)
            total = 0
            for product, qty in items:
                OrderItem.objects.create(order=order, product=product, product_name=product.name, quantity=qty, price=product.price)
                product.stock -= qty
                product.save()
                total += product.price * qty
            order.total_price = total
            order.save()
            return order

        make_order(buyer1, addr1, [(earbuds, 1), (watch, 1)])
        make_order(buyer2, addr3, [(jacket, 2), (earbuds, 1)])
        make_order(buyer3, addr5, [(keyboard, 1), (boots, 1)])
        make_order(buyer4, addr6, [(yoga_mat, 1), (resistance_bands, 1), (shaker, 2)])
        make_order(buyer5, addr7, [(serum, 1), (moisturizer, 1), (sunscreen, 1), (lip_set, 1)])
        make_order(buyer1, addr2, [(atomic, 1), (sapiens, 1), (cook_book, 1)])
        make_order(buyer2, addr4, [(lego, 1), (puzzle, 2)])
        make_order(buyer3, addr5, [(steel_watch, 1), (wallet, 1), (sunglasses, 1)])

        self.stdout.write(self.style.SUCCESS(
            f"\nDatabase seeded successfully!\n"
            f"  Categories : {Category.objects.count()}\n"
            f"  Sellers    : {User.objects.filter(role='Seller').count()}\n"
            f"  Buyers     : {User.objects.filter(role='Buyer').count()}\n"
            f"  Products   : {Product.objects.count()}\n"
            f"  Images     : {ProductImage.objects.count()}\n"
            f"  Orders     : {Order.objects.count()}\n"
            f"  Order Items: {OrderItem.objects.count()}\n"
        ))
