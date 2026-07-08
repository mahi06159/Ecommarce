from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Category, Product
from orders.models import Address, Order, OrderItem
from authentication.models import BuyerProfile, SellerProfile

User = get_user_model()

class Command(BaseCommand):
    help = "Seeds the database with e-commerce data (sellers, buyers, profiles, addresses, products, orders, items)."

    def handle(self, *args, **options):
        self.stdout.write("Clearing existing data...")
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Address.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        BuyerProfile.objects.all().delete()
        SellerProfile.objects.all().delete()
        User.objects.all().delete()

        self.stdout.write("Seeding categories...")
        electronics = Category.objects.create(name="Electronics")
        fashion = Category.objects.create(name="Fashion")
        home = Category.objects.create(name="Home & Kitchen")
        books = Category.objects.create(name="Books")

        self.stdout.write("Seeding users...")
        # 1. Create Sellers
        seller1 = User.objects.create_user(
            username="gadget_hub",
            email="seller1@example.com",
            password="password123",
            role="Seller"
        )
        # Update dynamically created profile
        sp1 = seller1.seller_profile
        sp1.store_name = "Gadget Hub Store"
        sp1.store_description = "Your one-stop shop for all things electronic."
        sp1.save()

        seller2 = User.objects.create_user(
            username="chic_wear",
            email="seller2@example.com",
            password="password123",
            role="Seller"
        )
        sp2 = seller2.seller_profile
        sp2.store_name = "Chic Wear Boutique"
        sp2.store_description = "Trendy fashion and clothing for all seasons."
        sp2.save()

        # 2. Create Buyers
        buyer1 = User.objects.create_user(
            username="john_doe",
            email="buyer1@example.com",
            password="password123",
            role="Buyer"
        )
        bp1 = buyer1.buyer_profile
        bp1.phone_number = "+1234567890"
        bp1.save()

        buyer2 = User.objects.create_user(
            username="alice_smith",
            email="buyer2@example.com",
            password="password123",
            role="Buyer"
        )
        bp2 = buyer2.buyer_profile
        bp2.phone_number = "+9876543210"
        bp2.save()

        buyer3 = User.objects.create_user(
            username="bob_jones",
            email="buyer3@example.com",
            password="password123",
            role="Buyer"
        )
        bp3 = buyer3.buyer_profile
        bp3.phone_number = "+1112223333"
        bp3.save()

        self.stdout.write("Seeding addresses...")
        # Addresses for Buyer 1
        addr1_1 = Address.objects.create(
            user=buyer1,
            address_line1="123 Main St",
            address_line2="Apt 4B",
            city="New York",
            state="NY",
            postal_code="10001",
            country="USA",
            is_default=True
        )
        addr1_2 = Address.objects.create(
            user=buyer1,
            address_line1="456 Work Ave",
            address_line2="Suite 300",
            city="San Francisco",
            state="CA",
            postal_code="94105",
            country="USA",
            is_default=False
        )

        # Addresses for Buyer 2
        addr2_1 = Address.objects.create(
            user=buyer2,
            address_line1="789 Pine Rd",
            city="Seattle",
            state="WA",
            postal_code="98101",
            country="USA",
            is_default=True
        )
        addr2_2 = Address.objects.create(
            user=buyer2,
            address_line1="101 Lake Dr",
            city="Bellevue",
            state="WA",
            postal_code="98004",
            country="USA",
            is_default=False
        )

        # Address for Buyer 3
        addr3_1 = Address.objects.create(
            user=buyer3,
            address_line1="202 Elm St",
            city="Austin",
            state="TX",
            postal_code="78701",
            country="USA",
            is_default=True
        )

        self.stdout.write("Seeding products...")
        # Products for Seller 1
        earbuds = Product.objects.create(
            seller=seller1,
            category=electronics,
            name="Wireless Earbuds",
            details="Premium noise-canceling wireless earbuds with long battery life.",
            price=49.99,
            stock=50
        )
        watch = Product.objects.create(
            seller=seller1,
            category=electronics,
            name="Smart Watch",
            details="Fitness tracking smartwatch with heart rate monitor.",
            price=129.99,
            stock=20
        )
        keyboard = Product.objects.create(
            seller=seller1,
            category=electronics,
            name="Mechanical Keyboard",
            details="RGB backlit mechanical keyboard with tactile blue switches.",
            price=79.99,
            stock=15
        )

        # Products for Seller 2
        jacket = Product.objects.create(
            seller=seller2,
            category=fashion,
            name="Denim Jacket",
            details="Classic stylish denim jacket made of premium cotton.",
            price=59.99,
            stock=30
        )
        boots = Product.objects.create(
            seller=seller2,
            category=fashion,
            name="Leather Boots",
            details="Handcrafted genuine leather boots designed for comfort and durability.",
            price=119.99,
            stock=10
        )
        tshirt = Product.objects.create(
            seller=seller2,
            category=fashion,
            name="Cotton T-Shirt",
            details="Breathable lightweight organic cotton T-shirt.",
            price=19.99,
            stock=100
        )

        self.stdout.write("Seeding orders...")
        # Order 1: Buyer 1 buys Wireless Earbuds and Smart Watch
        order1 = Order.objects.create(
            buyer=buyer1,
            shipping_address=addr1_1,
            shipping_address_text=str(addr1_1),
            total_price=0.00
        )
        OrderItem.objects.create(
            order=order1,
            product=earbuds,
            product_name=earbuds.name,
            quantity=1,
            price=earbuds.price
        )
        OrderItem.objects.create(
            order=order1,
            product=watch,
            product_name=watch.name,
            quantity=1,
            price=watch.price
        )
        # Update product stock
        earbuds.stock -= 1
        earbuds.save()
        watch.stock -= 1
        watch.save()
        # Compute order total
        order1.total_price = earbuds.price * 1 + watch.price * 1
        order1.save()

        # Order 2: Buyer 2 buys Denim Jacket and Wireless Earbuds
        order2 = Order.objects.create(
            buyer=buyer2,
            shipping_address=addr2_1,
            shipping_address_text=str(addr2_1),
            total_price=0.00
        )
        OrderItem.objects.create(
            order=order2,
            product=jacket,
            product_name=jacket.name,
            quantity=2,
            price=jacket.price
        )
        OrderItem.objects.create(
            order=order2,
            product=earbuds,
            product_name=earbuds.name,
            quantity=1,
            price=earbuds.price
        )
        jacket.stock -= 2
        jacket.save()
        earbuds.stock -= 1
        earbuds.save()
        order2.total_price = jacket.price * 2 + earbuds.price * 1
        order2.save()

        # Order 3: Buyer 3 buys Mechanical Keyboard and Leather Boots
        order3 = Order.objects.create(
            buyer=buyer3,
            shipping_address=addr3_1,
            shipping_address_text=str(addr3_1),
            total_price=0.00
        )
        OrderItem.objects.create(
            order=order3,
            product=keyboard,
            product_name=keyboard.name,
            quantity=1,
            price=keyboard.price
        )
        OrderItem.objects.create(
            order=order3,
            product=boots,
            product_name=boots.name,
            quantity=1,
            price=boots.price
        )
        keyboard.stock -= 1
        keyboard.save()
        boots.stock -= 1
        boots.save()
        order3.total_price = keyboard.price * 1 + boots.price * 1
        order3.save()

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
