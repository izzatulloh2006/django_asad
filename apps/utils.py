from .models import Product, OrderProduct, Order, Customer
from django.contrib import messages

class CartForAuthenticatedUser:
    def __init__(self, request, pk=None, action=None):
        self.user = request.user
        self.request = request

        if pk and action:
            self.add_or_delete(pk, action)


    # Метод для получения информации о корзине
    def get_cart_info(self):
        customer, created = Customer.objects.get_or_create(user=self.user)

        order, created = Order.objects.get_or_create(customer=customer)
        order_products = order.orderproduct_set.all()

        cart_total_quantity = order.get_cart_total_quantity
        cart_total_price = order.get_cart_total_price

        return {
            'cart_total_quantity': cart_total_quantity,
            'cart_total_price': cart_total_price,
            'order': order,
            'products': order_products
        }


    # Метод который будит добавлять или удалять товар из корзины
    def add_or_delete(self, pk, action):
        order = self.get_cart_info()['order']
        product = Product.objects.get(pk=pk)
        order_product, created = OrderProduct.objects.get_or_create(order=order, product=product)

        if action == 'add' and product.quantity > 0:
            order_product.quantity += 1  # +1 в корзину
            product.quantity -= 1  # -1 у кол-ва товара
            messages.success(self.request, f'Товар {product.title} в корзине')
        else:
            order_product.quantity -= 1  # -1 в корзине
            product.quantity += 1  # +1 у кол-ва товара
            messages.warning(self.request, f'Товар {product.title} удалён из корзины')

        product.save()
        order_product.save()


        if order_product.quantity <= 0:
            order_product.delete()


    # Метод для очищения корзины после заказа
    def clear(self):
        order = self.get_cart_info()['order']
        order_products = order.orderproduct_set.all()
        for product in order_products:
            product.delete()

        order.save()


# Функция для получения информации о крзине
def get_cart_data(request):
    cart = CartForAuthenticatedUser(request)
    cart_info = cart.get_cart_info()
    return cart_info

