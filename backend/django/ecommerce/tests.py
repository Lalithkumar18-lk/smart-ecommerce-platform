from django.test import TestCase
from ecommerce.models import Product


class ProductModelTests(TestCase):
    def test_create_product(self):
        product = Product.objects.create(
            name="Test Headphones",
            category="Electronics",
            price="2499.00",
            stock=10,
        )
        self.assertEqual(product.name, "Test Headphones")
        self.assertEqual(product.stock, 10)
        self.assertTrue(product.is_active)
