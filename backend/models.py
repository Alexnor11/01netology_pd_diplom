from django.conf import settings
from django.db import models


class Shop(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название магазина')
    url = models.URLField(null=True, blank=True, verbose_name='Ссылка')

    # filename
    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Список магазинов'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Category(models.Model):
    shops = models.ManyToManyField(Shop,
                                   related_name='categories',
                                   blank=True,
                                   verbose_name='Магазины')

    name = models.CharField(max_length=80, verbose_name='Название категории')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Список категорий'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=80, verbose_name='Название продукта')
    category = models.ForeignKey(Category, verbose_name='Категория', related_name='products', blank=True,
                                 on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = "Список продуктов"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    product = models.ForeignKey(Product, verbose_name='Продукт', related_name='product_infos', blank=True,
                                on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='product_infos', blank=True,
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name="Название")
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Рекомендуемая розничная цена')

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = "Информационный список о продуктах"
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop', 'external_id'], name='unique_product_info'),
        ]


class Parameter(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название')

    class Meta:
        verbose_name = 'Имя параметра'
        verbose_name_plural = "Список имен параметров"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, verbose_name='Информация о продукте',
                                     related_name='product_parameters', blank=True,
                                     on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, verbose_name='Параметр', related_name='product_parameters', blank=True,
                                  on_delete=models.CASCADE)
    value = models.CharField(verbose_name='Значение', max_length=100)

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = "Список параметров"
        constraints = [
            models.UniqueConstraint(fields=['product_info', 'parameter'], name='unique_product_parameter'),
        ]


class Order(models.Model):
    STATE_CHOICES = (
        ('basket', 'Корзина'),
        ('new', 'Новый'),
        ('confirmed', 'Подтвержден'),
        ('assembled', 'Собран'),
        ('sent', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('canceled', 'Отменен'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь", related_name='orders')
    dt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=STATE_CHOICES, verbose_name="Текущий статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Заказ создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Время последнего изменения статуса")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ('-created_at',)

    def __str__(self):
        return f'Создан: {self.created_at}, статус: {self.status}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name="ordered_items", blank=True, verbose_name="Заказ")
    product = models.ForeignKey(ProductInfo, on_delete=models.CASCADE,
                                related_name="in_orders", blank=True, verbose_name="Продукт")
    quantity = models.PositiveIntegerField(verbose_name="Количество", default=1)

    class Meta:
        verbose_name = "Позиция в заказе"
        verbose_name_plural = "Позиции в заказе"
        unique_together = ("order", "product")

    def __str__(self):
        return f'{self.product} - {self.quantity}'

