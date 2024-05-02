from django import template
from digital.models import Product, Category, FavoriteProducts


register = template.Library()


# Функция которая будит возвращать последний товар категории

@register.simple_tag()
def get_products(category):
    products = Product.objects.filter(category=category)[::-1]
    return products

# Функция которая будит возвращать категории на html
@register.simple_tag()
def get_categories():
    return Category.objects.filter(parent=None)

# Функция для полученяи цветов товара модели

@register.simple_tag()
def get_colors(model_product):
    products = Product.objects.filter(model_product=model_product)
    list_colors = [i.color_code for i in products]
    return list_colors



# Функция для получения нормальной цены
@register.simple_tag()
def get_normal_price(price):
    return f'{int(price):_}'.replace('_', ' ')

@register.simple_tag()
def get_favorite_products(user):
    fav_products = FavoriteProducts.objects.filter(user=user)
    products = [i.product for i in fav_products]
    return products


