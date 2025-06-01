import random
from faker import Faker

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction

from main.models import Employee, Category, Product, Supplier, Inventory, Sale

fake = Faker()

class Command(BaseCommand):
    help = 'Generate fake data for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("🟡 Starting fake data generation..."))
        try:
            self.create_employees()
            self.create_categories()
            self.create_suppliers()
            self.create_products()
            self.create_inventories()
            self.create_sales()
            self.stdout.write(self.style.SUCCESS("✅ Successfully generated all fake data!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ An error occurred: {str(e)}"))

    def create_employees(self, n=50):
        self.stdout.write("➡ Creating employees...")
        for _ in range(n):
            try:
                with transaction.atomic():
                    username = fake.user_name()
                    while User.objects.filter(username=username).exists():
                        username = fake.user_name()

                    user = User.objects.create_user(
                        username=username,
                        email=fake.email(),
                        password='password123'
                    )
                    Employee.objects.create(
                        user=user,
                        name=fake.name(),
                        position=fake.job(),
                        phone=fake.phone_number(),
                        email=user.email
                    )
            except Exception as e:
                self.stdout.write(f"⚠ Error creating employee: {str(e)}")

    def create_categories(self):
        self.stdout.write("➡ Creating categories...")
        categories = ['Men', 'Women', 'Kids', 'Accessories', 'Shoes']
        for name in categories:
            try:
                Category.objects.get_or_create(name=name)
            except Exception as e:
                self.stdout.write(f"⚠ Error creating category {name}: {str(e)}")

    def create_suppliers(self, n=50):
        self.stdout.write("➡ Creating suppliers...")
        for _ in range(n):
            try:
                Supplier.objects.create(
                    name=fake.company(),
                    contact_person=fake.name(),
                    phone=fake.phone_number(),
                    email=fake.company_email(),
                    address=fake.address()
                )
            except Exception as e:
                self.stdout.write(f"⚠ Error creating supplier: {str(e)}")

    def create_products(self, n=200):
        self.stdout.write("➡ Creating products...")
        categories = list(Category.objects.all())
        if not categories:
            self.stdout.write("❗ No categories found. Please create categories first.")
            return

        for _ in range(n):
            try:
                Product.objects.create(
                    name=fake.word().capitalize() + " " + fake.color_name(),
                    category=random.choice(categories),
                    size=random.choice(['S', 'M', 'L', 'XL', 'XXL']),
                    color=fake.color_name(),
                    price=round(random.uniform(10, 200), 2),
                    stock_quantity=random.randint(0, 100)
                )
            except Exception as e:
                self.stdout.write(f"⚠ Error creating product: {str(e)}")

    def create_inventories(self, n=200):
        self.stdout.write("➡ Creating inventories...")
        products = list(Product.objects.all())
        suppliers = list(Supplier.objects.all())

        if not products or not suppliers:
            self.stdout.write("❗ No products or suppliers found. Please create them first.")
            return

        for _ in range(n):
            try:
                with transaction.atomic():
                    product = random.choice(products)
                    quantity = random.randint(1, 50)
                    Inventory.objects.create(
                        product=product,
                        supplier=random.choice(suppliers),
                        quantity=quantity,
                        unit_price=product.price
                    )
            except Exception as e:
                self.stdout.write(f"⚠ Error creating inventory: {str(e)}")

    def create_sales(self, n=1000):
        self.stdout.write("➡ Creating sales...")
        products = list(Product.objects.all())
        employees = list(Employee.objects.all())

        if not products or not employees:
            self.stdout.write("❗ No products or employees found. Please create them first.")
            return

        for _ in range(n):
            try:
                with transaction.atomic():
                    product = random.choice(products)
                    if product.stock_quantity > 0:
                        quantity = random.randint(1, min(2, product.stock_quantity))
                        employee = random.choice(employees)
                        Sale.objects.create(
                            product=product,
                            employee=employee,
                            quantity=quantity,
                            price=product.price
                        )
                        product.stock_quantity -= quantity
                        product.save()
            except Exception as e:
                self.stdout.write(f"⚠ Error creating sale: {str(e)}")
