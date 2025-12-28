from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import random
from datetime import timedelta

# Import your models
from apps.users.models import User, Address
from apps.products.models import Category, Product
from apps.orders.models import Order, OrderItem
from apps.reviews.models import Review
from apps.cart.models import Cart, CartItem

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with dummy e-commerce data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Creating dummy data...')
        
        # Create data in order of dependencies
        users = User.objects.all()
        self.stdout.write(self.style.SUCCESS(f'Created {len(users)} users'))

        addresses = self.create_addresses(users)
        self.stdout.write(self.style.SUCCESS(f'Created {len(addresses)} addresses'))
        
        categories = self.create_categories()
        self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} categories'))
        
        products = self.create_products(categories)
        self.stdout.write(self.style.SUCCESS(f'Created {len(products)} products'))
        
        orders = self.create_orders(users, products, addresses)
        self.stdout.write(self.style.SUCCESS(f'Created {len(orders)} orders'))
        
        reviews = self.create_reviews(users, products)
        self.stdout.write(self.style.SUCCESS(f'Created {len(reviews)} reviews'))
        
        carts = self.create_carts(users, products)
        self.stdout.write(self.style.SUCCESS(f'Created {len(carts)} carts'))
        
        self.stdout.write(self.style.SUCCESS('Successfully populated database!'))

    def clear_data(self):
        """Clear existing data"""
        Review.objects.all().delete()
        CartItem.objects.all().delete()
        Cart.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Address.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def create_users(self):
        """Create dummy users"""
        users = []
        
        # Create admin user
        if not User.objects.filter(email='admin@example.com').exists():
            admin = User.objects.create_superuser(
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            users.append(admin)
        
        # Create vendors
        vendor_data = [
            ('vendor1@example.com', 'John', 'Vendor1'),
            ('vendor2@example.com', 'Jane', 'Vendor2'),
        ]
        
        for email, first_name, last_name in vendor_data:
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    email=email,
                    password='password123',
                    first_name=first_name,
                    last_name=last_name,
                    role='vendor'
                )
                users.append(user)
        
        # Create customers
        customer_data = [
            ('alice@example.com', 'Alice', 'Johnson'),
            ('bob@example.com',  'Bob', 'Smith'),
            ('charlie@example.com',  'Charlie', 'Brown'),
            ('diana@example.com',  'Diana', 'Wilson'),
            ('eve@example.com',  'Eve', 'Davis'),
        ]
        
        for email, first_name, last_name in customer_data:
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    email=email,
                    password='password123',
                    first_name=first_name,
                    last_name=last_name,
                    role='customer'
                )
                users.append(user)
        
        return users

    def create_addresses(self, users):
        """Create dummy addresses for users"""
        addresses = []
        address_templates = [
            {
                'address_line1': '123 Main St',
                'city': 'New York',
                'state': 'NY',
                'zip_code': '10001',
                'country': 'USA'
            },
            {
                'address_line1': '456 Oak Ave',
                'city': 'Los Angeles',
                'state': 'CA',
                'zip_code': '90001',
                'country': 'USA'
            },
            {
                'address_line1': '789 Pine Rd',
                'city': 'Chicago',
                'state': 'IL',
                'zip_code': '60601',
                'country': 'USA'
            },
        ]
        
        customers = [u for u in users if u.role == 'customer']
        
        for user in customers:
            # Create 1-2 addresses per customer
            for i in range(random.randint(1, 2)):
                template = random.choice(address_templates)
                address = Address.objects.create(
                    user=user,
                    full_name=f"{user.first_name} {user.last_name}",
                    phone=f"+1555{random.randint(1000000, 9999999)}",
                    address_line1=template['address_line1'],
                    city=template['city'],
                    state=template['state'],
                    zip_code=template['zip_code'],
                    country=template['country'],
                    is_default=(i == 0)
                )
                addresses.append(address)
        
        return addresses

    def create_categories(self):
        """Create product categories"""
        categories_data = [
            ('Electronics', 'Electronic devices and accessories'),
            ('Clothing', 'Fashion and apparel'),
            ('Books', 'Books and educational materials'),
            ('Home & Garden', 'Home improvement and garden supplies'),
            ('Sports', 'Sports equipment and fitness'),
            ('Toys', 'Toys and games'),
            ('Beauty', 'Beauty and personal care'),
            ('Food', 'Food and beverages'),
        ]
        
        categories = []
        for name, description in categories_data:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            categories.append(category)
        
        return categories

    def create_products(self, categories):
        """Create dummy products"""
        products_data = [
            # Electronics
            ('Smartphone XYZ', 'Latest smartphone with advanced features', 699.99, 'Electronics', 50),
            ('Laptop Pro 15', 'High-performance laptop for professionals', 1299.99, 'Electronics', 30),
            ('Wireless Headphones', 'Noise-canceling wireless headphones', 199.99, 'Electronics', 100),
            ('Smart Watch', 'Fitness tracking smart watch', 299.99, 'Electronics', 75),
            ('Tablet 10"', 'Portable tablet with high-resolution display', 449.99, 'Electronics', 60),
            
            # Clothing
            ('Men\'s T-Shirt', 'Comfortable cotton t-shirt', 19.99, 'Clothing', 200),
            ('Women\'s Jeans', 'Classic blue denim jeans', 59.99, 'Clothing', 150),
            ('Sneakers', 'Athletic running sneakers', 89.99, 'Clothing', 100),
            ('Winter Jacket', 'Warm winter jacket with hood', 149.99, 'Clothing', 80),
            ('Summer Dress', 'Light and breezy summer dress', 39.99, 'Clothing', 120),
            
            # Books
            ('Python Programming Guide', 'Comprehensive Python programming book', 34.99, 'Books', 100),
            ('Fiction Novel', 'Bestselling fiction novel', 14.99, 'Books', 150),
            ('Cookbook', 'Recipes from around the world', 24.99, 'Books', 80),
            
            # Home & Garden
            ('Coffee Maker', 'Programmable coffee maker', 79.99, 'Home & Garden', 50),
            ('Garden Tool Set', 'Complete set of garden tools', 49.99, 'Home & Garden', 60),
            ('Bed Sheets Set', 'Luxury cotton bed sheets', 69.99, 'Home & Garden', 90),
            
            # Sports
            ('Yoga Mat', 'Non-slip exercise yoga mat', 29.99, 'Sports', 150),
            ('Dumbbell Set', '20lb adjustable dumbbell set', 99.99, 'Sports', 40),
            ('Tennis Racket', 'Professional tennis racket', 149.99, 'Sports', 30),
            
            # Toys
            ('Building Blocks Set', 'Educational building blocks', 34.99, 'Toys', 100),
            ('Action Figure', 'Collectible action figure', 19.99, 'Toys', 200),
        ]
        
        products = []
        for name, description, price, category_name, stock in products_data:
            category = Category.objects.get(name=category_name)
            
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'price': Decimal(str(price)),
                    'category': category,
                    'stock': stock,
                    'is_active': True,
                    'created_by_id': 7
                }
            )
            products.append(product)
        
        return products

    def create_orders(self, users, products, addresses):
        """Create dummy orders"""
        orders = []
        customers = [u for u in users if u.role == 'customer']
        
        order_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        
        for customer in customers:
            # Create 1-3 orders per customer
            num_orders = random.randint(1, 3)
            customer_addresses = Address.objects.filter(user=customer)
            
            if not customer_addresses.exists():
                continue
                
            for _ in range(num_orders):
                order = Order.objects.create(
                    user=customer,
                    status=random.choice(order_statuses),
                    shipping_address=str(random.choice(customer_addresses)),
                    subtotal=Decimal('0.00'),
                    total=Decimal('0.00'),   
                    created_at=timezone.now() - timedelta(days=random.randint(1, 90))
                )
                
                # Add 1-4 items to each order
                num_items = random.randint(1, 4)
                order_total = Decimal('0.00')
                
                for _ in range(num_items):
                    product = random.choice(products)
                    quantity = random.randint(1, 3)
                    price = product.price
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        product_price=price
                    )
                    
                    order_total += price * quantity
                
                order.total = order_total
                order.save()
                orders.append(order)
        
        return orders

    
    def create_reviews(self, users, products):
        """Create product reviews"""
        reviews = []
        customers = [u for u in users if u.role == 'customer']
        
        review_texts = [
            "Great product! Highly recommend.",
            "Good quality for the price.",
            "Exceeded my expectations!",
            "Decent product, does the job.",
            "Not bad, but could be better.",
            "Amazing! Will buy again.",
            "Perfect! Exactly what I needed.",
        ]
        
        for product in random.sample(products, min(15, len(products))):
            # Create 1-3 reviews per product
            num_reviews = random.randint(1, 3)
            
            for _ in range(num_reviews):
                customer = random.choice(customers)
                
                # Check if review already exists
                if not Review.objects.filter(user=customer, product=product).exists():
                    review = Review.objects.create(
                        user=customer,
                        product=product,
                        rating=random.randint(3, 5),
                        comment=random.choice(review_texts),
                        created_at=timezone.now() - timedelta(days=random.randint(1, 60))
                    )
                    reviews.append(review)
        
        return reviews

    def create_carts(self, users, products):
        """Create shopping carts with items"""
        carts = []
        customers = [u for u in users if u.role == 'customer']
        
        # Create active carts for some customers
        for customer in random.sample(customers, min(3, len(customers))):
            cart, created = Cart.objects.get_or_create(user=customer)
            
            # Add 1-3 items to cart
            num_items = random.randint(1, 3)
            
            for _ in range(num_items):
                product = random.choice(products)
                
                CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={'quantity': random.randint(1, 3)}
                )
            
            carts.append(cart)
        
        return carts