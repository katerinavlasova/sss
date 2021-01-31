from products.models import Product
from myapp.models import Customer
from orders.models import Order

class ProductBuilder:
	def __init__(self, slug):
		self.product = Product.objects.create(slug=slug)
	def with_name(self, name):
		self.product.name = name
		return self
	def with_copies(self,copies):
		self.product.copies = copies
		return self
	def with_brand(self,brand):
		self.product.brand = brand
		return self
	def with_series(self,series):
		self.product.series = series
		return self
	def with_category(self,category):
		self.product.category = category
	def with_price(self, price):
		self.product.price = price
		return self
	def with_discount(self, discount):
		self.product.discount = discount
		return self
	def with_is_active(self, is_active):
		self.product.is_active = is_active
		return self
	def with_color(self, color):
		self.product.color = color
		return self
	def with_weight(self, weight):
		self.product.weight = weight
		return self
	def with_country(self, country):
		self.product.country = country
		return self
	def with_guarantee(self, guarantee):
		self.product.guarantee = guarantee
		return self
	def with_desctiption(self, description):
		self.product.description = description
		return self
		
		
class CustomerBuilder:
	def __init__(self, user):
		self.customer = Customer.objects.create(user=user)
	def with_first_name(self, first_name):
		self.customer.first_name = first_name
		return self
	def with_last_name(self, last_name):
		self.customer.last_name = last_name
		return self
	def with_email(self, email):
		self.customer.email = email
		return self
	def with_phone(self, phone):
		self.customer.phone = phone
		return self
	def with_address(self, address):
		self.customer.address = address
		return self
		
		
class OrderBuilder:
	def __init__(self, customer):
		self.order = Order.objects.create(customer=customer)
	def with_total_price(self, total_price):
		self.order.total_price = total_price
		return self
	def with_comment(self, comment):
		self.order.commets = comment
		return self
	def with_status(self, status):
		self.order.status = status
		return self
