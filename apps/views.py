from random import randint

from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from .models import *
from django.views.generic import ListView, DetailView
from .forms import LoginForm, RegisterForm, CustomerForm, ShippingForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import CartForAuthenticatedUser, get_cart_data
import stripe


# Create your views here.

class ProductList(ListView):
    model = Product
    context_object_name = 'categories'

    extra_context = {
        'title': 'DigitalStore'
    }

    template_name = 'digital/index.html'

    def get_queryset(self):
        categories = Category.objects.filter(parent=None)
        return categories


# Вьюшка для страницы категории товаров
class CategoryView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'digital/category.html'
    paginate_by = 1

    def get_queryset(self):


        category = Category.objects.get(slug=self.kwargs['slug'])
        products = Product.objects.filter(category=category)


        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        category = Category.objects.get(slug=self.kwargs['slug'])
        context['title'] = f'Категория {category.title}'
        context['category'] = category

        return context


# Функция для страницы входа в Аккаунт и логика входа
def user_login_view(request):
    if request.user.is_authenticated:
        page = request.META.get('HTTP_REFERER', 'index')
        return redirect(page)
    else:
        if request.method == 'POST':
            form = LoginForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                if user:
                    login(request, user)
                    messages.success(request, 'Вы вошли в Аккаунт')
                    return redirect('index')
                else:
                    messages.error(request, 'Не верный логин или пароль')
                    return redirect('login')
            else:
                messages.error(request, 'Не верный логин или пароль')
                return redirect('login')
        else:
            form = LoginForm()

        context = {
            'form': form,
            'title': 'Вход в Аккаунт'
        }

        return render(request, 'digital/login.html', context)


# Вьюшка для выхода из аккаунта
def user_logout_view(request):
    logout(request)
    messages.warning(request, 'Уже уходите 😢')
    return redirect('index')


# Вьюшка для страницы регистрации
def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == 'POST':
            form = RegisterForm(data=request.POST)
            if form.is_valid():
                user = form.save()
                messages.success(request, 'Регистрация прошла успешно. Авторизуйтесь')
                return redirect('login')
            else:
                for field in form.errors:
                    messages.error(request, form.errors[field].as_text())
                    return redirect('register')

        else:
            form = RegisterForm()

        context = {
            'form': form,
            'title': 'Регистрация пользователя'
        }

        return render(request, 'digital/register.html', context)


# Вьюшка для страницы детали товара
class ProductDetail(DetailView):
    model = Product
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        product = Product.objects.get(slug=self.kwargs['slug'])
        context['title'] = f'Товар {product.title}'

        products = Product.objects.filter(category=product.category)
        data = []
        for i in range(0, 3):
            random_index = randint(0, len(products) - 1)
            p = products[random_index]
            if p not in data and product != p:
                data.append(p)

        context['products'] = data

        return context


# Вьюшка для получения товара по цвету
def product_by_color(request, model_product, color_code):
    product = Product.objects.get(model_product=model_product, color_code=color_code)

    products = Product.objects.filter(category=product.category)
    data = []
    for i in range(0, 3):
        random_index = randint(0, len(products) - 1)
        p = products[random_index]
        if p not in data and product != p:
            data.append(p)

    context = {
        'title': f'Товар {product.title}',
        'product': product,
        'products': data
    }

    return render(request, 'digital/product_detail.html', context)


# Вьюшка для добавления товара в избранное
def save_favorite_product(request, slug):
    if request.user.is_authenticated:
        user = request.user
        product = Product.objects.get(slug=slug)
        favorite_products = FavoriteProducts.objects.filter(user=user)
        if user:
            if product not in [i.product for i in favorite_products]:
                messages.success(request, f'Товар добавлен в избранное')
                FavoriteProducts.objects.create(user=user, product=product)
            else:
                fav_product = FavoriteProducts.objects.get(user=user, product=product)
                messages.error(request, f'Товар удалён из избранного')
                fav_product.delete()

            page = request.META.get('HTTP_REFERER', 'index')
            return redirect(page)

    else:
        messages.warning(request, 'Авторизуйтесь что бы добавить в избранное')
        return redirect('login')


# Вьюшка для страницы избранного
class FavoriteProductView(LoginRequiredMixin, ListView):
    model = FavoriteProducts
    template_name = 'digital/favorite.html'
    context_object_name = 'products'
    login_url = 'login'

    def get_queryset(self):
        user = self.request.user
        favorite_products = FavoriteProducts.objects.filter(user=user)
        products = [i.product for i in favorite_products]
        return products


# Вьюшка для добавления товара в корзину
def to_cart_view(request, pk, action):
    if request.user.is_authenticated:
        user_cart = CartForAuthenticatedUser(request, pk, action)
        page = request.META.get('HTTP_REFERER', 'index')
        return redirect(page)

    else:
        return redirect('login')


# Вьюшка для страницы каорзины пользователя
def my_cart_view(request):
    if request.user.is_authenticated:
        cart_info = get_cart_data(request)
        context = {
            'title': 'Моя корзина',
            'order': cart_info['order'],
            'products': cart_info['products']
        }
        return render(request, 'digital/my_cart.html', context)

    else:
        return redirect('login')


# Вьюшка для очтщения корзины кнопки
def clear_cart(request):
    user_cart = CartForAuthenticatedUser(request)
    order = user_cart.get_cart_info()['order']
    order_products = order.orderproduct_set.all()
    for order_product in order_products:
        quantity = order_product.quantity
        product = order_product.product
        order_product.delete()
        product.quantity += quantity
        product.save()
    messages.warning(request, 'Корзина очищена')
    return redirect('my_cart')


# Вьюшка для страницы оформления заказа
def checkout_view(request):
    if request.user.is_authenticated:
        cart_info = get_cart_data(request)

        context = {
            'title': 'Оформление заказа',
            'order': cart_info['order'],
            'items': cart_info['products'],

            'customer_form': CustomerForm(),
            'shipping_form': ShippingForm()
        }
        return render(request, 'digital/checkout.html', context)

    else:
        return redirect('login')


# Вьюшка для реализации оплаты
def create_checkout_session(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        user_cart = CartForAuthenticatedUser(request)
        cart_info = user_cart.get_cart_info()

        customer_form = CustomerForm(data=request.POST)  # Из формы пользователя получ данные
        if customer_form.is_valid():
            customer = Customer.objects.get(user=request.user)  # Получ покупателя по запросу пользователя
            customer.first_name = customer_form.cleaned_data['first_name']  # Получ имя покупателя из формы
            customer.last_name = customer_form.cleaned_data['last_name']  # Получ фамилию покупателя из формы
            customer.email = customer_form.cleaned_data['email']  # Получ посту покупателя из формы
            customer.save()

        shipping_form = ShippingForm(data=request.POST)
        if shipping_form.is_valid():
            address = shipping_form.save(commit=False)
            address.customer = Customer.objects.get(user=request.user)
            address.order = user_cart.get_cart_info()['order']
            address.save()
        else:
            for field in shipping_form.errors:
                messages.error(request, shipping_form.errors[field].as_text() )

        total_price = cart_info['cart_total_price']  # Получаем сумму заказа
        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data':{
                    'currency': 'uzs',
                    'product_data':{
                        'name': 'Товары DigitalStore'
                    },
                    'unit_amount': int(total_price)
                },
                'quantity': 1
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('success')),
            cancel_url=request.build_absolute_uri(reverse('checkout'))
        )
        return redirect(session.url, 303)



# Вьюшка для страницы успешной оплаты
def success_payment(request):
    if request.user.is_authenticated:
        user_cart = CartForAuthenticatedUser(request)
        # Дописать логику сохранения заказа

        user_cart.clear()
        messages.success(request, 'Ваша оплта прошла успешно. Мы вас кинули')
        return render(request, 'digital/success.html')

    else:
        return redirect('index')
