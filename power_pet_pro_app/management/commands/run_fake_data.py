from faker import Faker
from django.core.management.base import BaseCommand
from power_pet_pro_app.models import Product, Category
import random

STORE = {
    # Category : {products:[]}
    'Automotive': {
        'products': [
            'Auto Parts',
            'Tires',
            'Companies with Auto Services',
            'Motorcycle & ATV Parts and Gear',
        ]
    },
    'Baby & Toddler': {
        'products': [
            'Baby Furniture',
            'Baby Gear',
            'Baby Care & Safety',
        ]
    },
    'Clothing & Shoes': {
        'products': [
            'Baby Clothing',
            'Shoes',
            'Jewerly',
            'Watches',
            'Clothing Accessories',
            'Costumes',
            'Kid\'s Clothing',
            'Women\'s Clothing',
            'Men\'s Clothing',
            'Handbangs',
            'Uniforms & Scrubs',
            'Teen Clothing'
        ]
    },
    'Computers': {
        'products': [
            'Laptops',
            'Desktop Computers',
            'Computer Monitors',
            'Laptop Bags',
            'Hardware & Peripherals'
        ]
    },
    'Electronics': {
        'products': [
            'Video Games & Consoles',
            'Cameras & Camcorders',
            'Televisions',
            'MP3 & Media Players',
        ]
    },
    'Entertainment & Arts': {
        'products': [
            'Companies with Tickets',
            'Media',
            'Collectibles',
            'Toys & Games',
            'Crafts & Fabrics',
        ]
    },
    'Food & Gifts': {
        'products': [
            'Speciality Food',
            'Flower Delivery',
            'Personalized Gifts',
            'Stationery & Cards',
        ]
    },
    'Health & Beauty': {
        'products': [
            'Personal Care',
            'Cosmetics',
            'Supplements',
            'Hair Care',
            'Fragrances',
            'Skin care'
        ]
    },

}


class Command(BaseCommand):
    help = 'Building Product and Category data'

    def handle(self, *args, **options):
        # build faker
        fake = Faker()
        # Note that products itself is the dictionary so access the key 'products' to grab the list of items
        for category, products in STORE.items():
            # lets register the categories
            new_category = Category.objects.create(name=category)
            new_category.save()
            print('Registered Category: ' + category)

            # lets build our products
            for product in products['products']:
                new_product = Product.objects.create(
                    category=new_category,
                    name=product,
                    description=fake.paragraph(nb_sentences=5, variable_nb_sentences=False),
                    price=random.randint(1, 300),
                )
                new_product.save()
                print('New product added: ' + product)

