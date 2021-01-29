#from unittest import TestCase, mock
from django.test import TestCase
#from unittest.mock import patch, MagicMock, Mock
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coursework.settings")
django.setup()
#import sys
#sys.path.insert(1, 'myapp/')
#from views.py import Search
#from myapp.views.py import Search

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
		huaw = Product.objects.create(name='Huawei Y6', copies = 4, brand = 'Huawei', series='Y6', category = 'Laptop', price=400000,discount=0,is_active=True, color='Black',weight='200',country='India', guarantee='3', description='goodgodd',slug='slughuawei')
	def test_name_label(self):
		product = Product.objects.get(slug='slughuawei')
		name_label = Product._meta.get_field('name').verbose_name
		self.assertEqual(name_label, 'name')
	def test_name_maxlength(self):
		product = Product.objects.get(slug='slughuawei')
		max_length = Product._meta.get_field('name').max_length
		self.assertEqual(max_length, 30)
	def test_copies_label(self):
		product = Product.objects.get(slug='slughuawei')
		field_label = Product._meta.get_field('copies').verbose_name
		self.assertEqual(field_label, 'copies')
	def test_copies_default(self):
		product = Product.objects.get(slug='slughuawei')
		defaultcount = Product._meta.get_field('copies').default
		self.assertEqual(defaultcount, 0)
	def test_brand_label(self):
		product = Product.objects.get(slug='slughuawei')
		field_label = Product._meta.get_field('brand').verbose_name
		self.assertEqual(field_label, 'brand')	
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
		cls.customer = Customer.objects.create(user=cls.user, first_name='Ivan', last_name='Ivanov',email='emailivana@mail.ru',phone='8800535353', address='Moscow')
	def test_firstname_label(self):
		cus = Customer.objects.get(email='emailivana@mail.ru')
		first_name_label = Customer._meta.get_field('first_name').verbose_name
		self.assertEqual(first_name_label, 'first name')
	def test_firstname_maxlength(self):
		cus = Customer.objects.get(email='emailivana@mail.ru')
		max_length = Customer._meta.get_field('first_name').max_length
		self.assertEqual(max_length, 20)
	def test_lastname_label(self):
		cus = Customer.objects.get(email='emailivana@mail.ru')
		last_name_label = Customer._meta.get_field('last_name').verbose_name
		self.assertEqual(last_name_label, 'last name')
	def test_lastname_maxlength(self):
		cus = Customer.objects.get(email='emailivana@mail.ru')
		max_length = Customer._meta.get_field('last_name').max_length
		self.assertEqual(max_length, 20)
	def test_email_label(self):
		cus = Customer.objects.get(email='emailivana@mail.ru')
		email_name_label = Customer._meta.get_field('email').verbose_name
		self.assertEqual(email_name_label, 'email')
	def test_getobjectname(self):
		cus = Customer.objects.get(email='emailivana@mail.ru')
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
		status = Status.objects.create(name="В обработке",is_active = True)
		order = Order.objects.create(customer=cls.customer, total_price=0,status=status,commets='comm')
	def test_price_default(self):
		order = Order.objects.get(customer=self.customer)
		defaultprice= Order._meta.get_field('total_price').default
		self.assertEqual(defaultprice, 0)
	def test_getobjectname(self):
		order = Order.objects.get(customer=self.customer)
		expected_object_name = 'Заказ %s %s' % (order.id, order.status)
		self.assertEqual(expected_object_name, str(order))
		
class TestProductInOrderModel(TestCase):
	@classmethod
	def setUpTestData(cls):
		user = User.objects.create_user(username='login', password='pass')
		cls.customer = Customer.objects.create(user=user, first_name='Ivan', last_name='Ivanov',email='emailivana@mail.ru',phone='8800535353', address='Moscow')
		status = Status.objects.create(name="В обработке",is_active = True)
		order = Order.objects.create(customer=cls.customer, total_price=0,status=status,commets='comm')
		productinorder = 
