#from unittest import TestCase, mock
from unittest import mock
from django.test import TestCase
from unittest.mock import MagicMock
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coursework.settings")
django.setup()
#import sys
#sys.path.insert(1, 'myapp/')
#from views.py import Search
#from myapp.views.py import Search

from builder import ProductBuilder

from myapp import views

from django.contrib.auth.models import User
from myapp.models import Customer
from myapp.managers import *
from myapp.views import login, logout
from django import forms
from django.contrib import auth
from django.urls import resolve
import requests

from orders.models import *
from myapp.views import add_to_order, Search

from products.models import Product
#class TestSearch(TestCase):
#	def setUp(self):
#		self.search = views.Search()
#	def test_0_hits(self):
#		self.search.get_queryset()
#	def test_1hit(self):
#		huaw = models.Product.objects.create(name='Huawei Y6', copies = 4, brand = 'Huawei', series='Y6', category = 'Laptop', price=400000,discount=0,is_active=True, color='Black',weight='200',country='India', guarantee='3', description='goodgodd',slug='slughuawei')
#		self.assertEqual(self.search.get_queryset.post('Huawei'), huaw)

class SessionStab:
	def flush(self):
		pass

class RequestStab:
	def __init__(self, user):
		self.user = user
		self.session = SessionStab()
	
class TestProductModel(TestCase):
	@classmethod
	def setUpTestData(cls):
		prod = ProductBuilder('slughuawei').with_name('Huawei Y6').with_copies(4).with_brand('Huawei').with_series('Y6').with_category('Laptop')
		#huaw = Product.objects.create(name='Huawei Y6', copies = 4, brand = 'Huawei', series='Y6', category = 'Laptop', price=400000,discount=0,is_active=True, color='Black',weight='200',country='India', guarantee='3', description='goodgodd',slug='slughuawei')

	def test_name_maxlength(self):
		product = Product.objects.get(slug='slughuawei')
		max_length = Product._meta.get_field('name').max_length
		self.assertEqual(max_length, 30)
	def test_copies_default(self):
		product = Product.objects.get(slug='slughuawei')
		defaultcount = Product._meta.get_field('copies').default
		self.assertEqual(defaultcount, 0)
	def test_brand_maxlength(self):
		product = Product.objects.get(slug='slughuawei')
		max_length = Product._meta.get_field('brand').max_length
		self.assertEqual(max_length, 40)
	def test_getobjectname(self):
		product = Product.objects.get(slug='slughuawei')
		expected_object_name = '%s' % (product.name)
		self.assertEqual(expected_object_name, str(product))
	def test_get_absolute_url(self):
		product = Product.objects.get(slug='slughuawei')
		self.assertEqual(product.get_absolute_url(), '/slughuawei/')

class TestCustomerModel(TestCase):
	@classmethod
	def setUpTestData(cls):
		cls.user = User.objects.create_user(username='login', password='pass')
		#cls.customer = CustomerBuilder(cls.user).with_first_name('Ivan').with_last_name('Ivanov').with_email('emailivana@mail.ru')
		cls.customer = Customer.objects.create(user=cls.user, first_name='Ivan', last_name='Ivanov',email='emailivana@mail.ru',phone='8800535353', address='Moscow')
	def test_firstname_maxlength(self):
		cus = Customer.objects.get(user=self.user)
		max_length = Customer._meta.get_field('first_name').max_length
		self.assertEqual(max_length, 20)
	def test_lastname_maxlength(self):
		cus = Customer.objects.get(user=self.user)
		max_length = Customer._meta.get_field('last_name').max_length
		self.assertEqual(max_length, 20)
	def test_getobjectname(self):
		cus = Customer.objects.get(user=self.user)
		expected_object_name = '%s %s' % (cus.email, cus.first_name)
		self.assertEqual(expected_object_name, str(cus))
	def test_not_auth(self):
		request_stab = RequestStab(self.user)
		#auth.
		logout(request_stab)
		cus = Customer.objects.get_authenticated(request_stab.user)
		self.assertIsNone(cus)
	def test_auth(self):
		us = auth.authenticate(username = 'login', password = 'pass')
		self.assertEqual(self.customer, Customer.objects.get_authenticated(us))

class TestOrderModel(TestCase):
	@classmethod
	def setUpTestData(cls):
		user = User.objects.create_user(username='login', password='pass')
		cls.customer = Customer.objects.create(user=user, first_name='Ivan', last_name='Ivanov',email='emailivana@mail.ru',phone='8800535353', address='Moscow')
		#RESERVED = "RES"
		#NEW = "NEW"
		#status_choices = ((RESERVED, "IN ORVER"), (NEW, "NEW"))
		cls.status = Status.objects.create(name="В обработке",is_active = True)
	def get_user(self):
		order = Order.objects.create(customer=self.customer, total_price=0,status=self.status,commets='comm')
		self.assertEqual(order.customer.user, self.customer.user)
	def test_price_default(self):
		order = Order.objects.create(customer=self.customer, total_price=0,status=self.status,commets='comm')
		defaultprice= Order._meta.get_field('total_price').default
		self.assertEqual(defaultprice, 0)
	def test_getobjectname(self):
		order = Order.objects.create(customer=self.customer, total_price=0,status=self.status,commets='comm')
		expected_object_name = 'Заказ %s %s' % (order.id, order.status)
		self.assertEqual(expected_object_name, str(order))
		
class TestProductInOrderModel(TestCase):
	@classmethod
	def setUpTestData(cls):
		user = User.objects.create_user(username='login', password='pass')
		cls.customer = Customer.objects.create(user=user, first_name='Ivan', last_name='Ivanov',email='emailivana@mail.ru',phone='8800535353', address='Moscow')
		status = Status.objects.create(name="В обработке",is_active = True)
		order = Order.objects.create(customer=cls.customer, total_price=0,status=status,commets='comm')
		product = Product.objects.create(name='Huawei Y6', copies = 4, brand = 'Huawei', series='Y6', category = 'Laptop', price=40000,discount=0,is_active=True, color='Black',weight='200',country='India', guarantee='3', description='goodgodd',slug='slughuawei')
		productinorder = ProductInOrder.objects.create(order=order,customer=cls.customer, product = product,number=2, is_active=True, price_per_item=40000,total_price=80000)
	def test_price_default(self):
		product = ProductInOrder.objects.get(customer=self.customer)
		defaultcount = ProductInOrder._meta.get_field('price_per_item').default
		self.assertEqual(defaultcount, 1)
	def test_number_default(self):
		product = ProductInOrder.objects.get(customer=self.customer)
		defaultcount = ProductInOrder._meta.get_field('number').default
		self.assertEqual(defaultcount, 0)
	def test_get_cost_one_prod(self):
		product = ProductInOrder.objects.get(customer=self.customer)
		product.number = 1
		product.save()
		self.assertEqual(product.get_cost(), 40000)
	def test_get_cost_two_prod(self):
		product = ProductInOrder.objects.get(customer=self.customer)
		self.assertEqual(product.get_cost(), 80000)
	def test_get_cost_two_prod_with_mock(self):
		expected_result = 80000
		product = ProductInOrder.objects.get(customer=self.customer)
		with mock.patch.object(ProductInOrder, 'get_cost', return_value = 80000):
			self.assertEqual(product.get_cost(), expected_result)
	def test_getobjectname(self):
		product = ProductInOrder.objects.get(customer=self.customer)
		expected_object_name = '%s' % (product.product.name)
		self.assertEqual(expected_object_name, str(product))

