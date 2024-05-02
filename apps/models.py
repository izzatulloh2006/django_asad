from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название категории')
    image = models.ImageField(upload_to='categories/', null=True, blank=True, verbose_name='Картинка')
    slug = models.SlugField(unique=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name='Категория', related_name='subcategories')

    def get_absolute_url(self):
        return reverse('category_page', kwargs={'slug': self.slug})

    # Метод для получения картинки категории
    def get_image_category(self):
        if self.image:
            return self.image.url
        else:
            return '-'

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'



# Модель товара
class Product(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название товара')
    price = models.FloatField(verbose_name='Цена')
    quantity = models.IntegerField(default=0, verbose_name='Количество')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    credit = models.CharField(max_length=250, null=True, blank=True, verbose_name='Рассрочка')
    discount = models.CharField(max_length=250, null=True, blank=True, verbose_name='Скидка')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products',
                                 verbose_name='Категория')
    slug = models.SlugField(unique=True, null=True)
    # memory = models.CharField(max_length=250,  verbose_name='Память')
    color_name = models.CharField(max_length=150, verbose_name='Навзание цыета')
    color_code = models.CharField(max_length=150, verbose_name='Код цвета')
    # brand = models.ForeignKey('Brand', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Бренд товара')
    length = models.CharField(max_length=100, null=True, blank=True, verbose_name='Длина')
    width = models.CharField(max_length=100, null=True, blank=True, verbose_name='Ширина')
    height = models.CharField(max_length=100, null=True, blank=True, verbose_name='Высота')
    # model_product = models.CharField(max_length=255, verbose_name='Модель', null=True, blank=True)



    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    # Метод для получения картинки товара
    def get_image_product(self):
        if self.images:
            try:
                return self.images.first().image.url
            except:
                return '-'
        else:
            return '-'

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


# Меодель Галереи картинок товаров
class Gallery(models.Model):
    image = models.ImageField(upload_to='products/', verbose_name='Картинка товара')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')

    class Meta:
        verbose_name = 'Картинка Товара'
        verbose_name_plural = 'Картинки Товаров'


# Модель описания товара
class ProductDescription(models.Model):
    parameter = models.CharField(max_length=150, verbose_name='Название параметра')
    parameter_info = models.CharField(max_length=400, verbose_name='Описание параметра')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар', related_name='parameters')

    class Meta:
        verbose_name = 'Описание Товара'
        verbose_name_plural = 'Описание Товаров'




class Brand(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название Бренда')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True,
                                 related_name='brand', verbose_name='Категория')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'




# Модел Избранное
class FavoriteProducts(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Избранный товар')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')

    def __str__(self):
        return f'Товар:{self.product}, пользователя: {self.user.username}'


    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные товары'


# -------------------------------------------------------------------------------------



# Модель покупателя
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, verbose_name='Покупатель')
    first_name = models.CharField(max_length=255, default='', verbose_name='Имя покупателя')
    last_name = models.CharField(max_length=255, default='', verbose_name='Фамилия покупателя')
    email = models.EmailField(verbose_name='Почта покупателя', blank=True, null=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'



# Моделька Заказа
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    is_completed = models.BooleanField(default=False, verbose_name='Выполнен ли заказ')
    shipping = models.BooleanField(default=True, verbose_name='Доставка')

    def __str__(self):
        return f'Заказа №: {self.pk}'


    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    # Метод для получения суммы заказа
    @property  # Декоратер чтобы можно было вызывать в другом классе
    def get_cart_total_price(self):
        order_products = self.orderproduct_set.all()
        total_price = sum([product.get_total_price for product in order_products])
        return total_price

    @property  # Декоратер чтобы можно было вызывать в другом классе
    def get_cart_total_quantity(self):
        order_products = self.orderproduct_set.all()
        total_quantity = sum([product.quantity for product in order_products])
        return total_quantity



# Модель Заказанных товаров

class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name='Товар')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, verbose_name='Заказ №')
    quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name='Количество')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    def __str__(self):
        return self.product.title


    class Meta:
        verbose_name = 'Заказанный товар'
        verbose_name_plural = 'Заказанные товары'

    # Метод для получения сумму зказанного товара
    @property
    def get_total_price(self):
        total_price = self.product.price * self.quantity
        return total_price



# Модель Доставки
class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=300, verbose_name='Адрес улица/дом')
    city = models.ForeignKey('City',  on_delete=models.CASCADE, verbose_name='Город доставки')
    region = models.CharField(max_length=255, verbose_name='Регион/Область')
    phone = models.CharField(max_length=255, verbose_name='Номер телефона')
    comment = models.CharField(max_length=500, verbose_name='Комментарий к заказу', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата доставки')


    def __str__(self):
        return f'Доставка заказа №:{self.order} по Адресу:{self.address}'

    class Meta:
        verbose_name = 'Адрес доставки'
        verbose_name_plural = 'Адреса доставок'




class City(models.Model):
    city_name = models.CharField(max_length=100, verbose_name='Название города')

    def __str__(self):
        return self.city_name

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
