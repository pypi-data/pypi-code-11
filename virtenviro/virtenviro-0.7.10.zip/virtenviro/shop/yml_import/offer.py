# ~*~ coding: utf-8 ~*~
__author__ = 'Kamo Petrosyan'


class Offer:
    """
    url
    URL страницы товара. Максимальная длина URL — 512 символов.
    Необязательный элемент для магазинов-салонов.

    price
    Цена, по которой данный товар можно приобрести. Цена товарного предложения округляется, формат, в котором она отображается, зависит от настроек пользователя.
    Обязательный элемент.

    oldprice
    Старая цена на товар, которая обязательно должна быть выше новой цены (<price>). Параметр <oldprice> необходим для автоматического расчета скидки на товар.
    Необязательный элемент.

    currencyId
    Идентификатор валюты товара (RUR, USD, UAH, KZT). Для корректного отображения цены в национальной валюте необходимо использовать идентификатор (например, UAH) с соответствующим значением цены.
    Обязательный элемент.

    categoryId
    Идентификатор категории товара, присвоенный магазином (целое число не более 18 знаков). Товарное предложение может принадлежать только одной категории.
    Обязательный элемент. Элемент <offer> может содержать только один элемент <categoryId>.

    market_category
    Категория товара, в которой он должен быть размещен на Яндекс.Маркете. Допустимо указывать названия категорий только из товарного дерева категорий Яндекс.Маркета.
    Необязательный элемент.
    Примечание. Скачать дерево категорий Яндекс.Маркета в формате XLS.

    picture
    Ссылка на картинку соответствующего товарного предложения. Недопустимо давать ссылку на «заглушку», т. е. на страницу, где написано «картинка отсутствует», или на логотип магазина. Максимальная длина URL — 512 символов.
    Необязательный элемент.

    store
    Элемент позволяет указать возможность купить соответствующий товар в розничном магазине.
    Возможные значения:
    1) false — возможность покупки в розничном магазине отсутствует;
    2) true — товар можно купить в розничном магазине.
    Необязательный элемент.

    pickup
    Элемент позволяет указать возможность зарезервировать выбранный товар и забрать его самостоятельно.
    Возможные значения:
    1) false — возможность «самовывоза» отсутствует;
    2) true — товар можно забрать самостоятельно.
    Необязательный элемент.

    delivery
    Элемент позволяет указать возможность доставки соответствующего товара.
    Возможные значения:
    1) false — товар не может быть доставлен;
    2) true — товар доставляется на условиях, которые описываются в партнерском интерфейсе на странице Параметры размещения.
    Необязательный элемент.

    local_delivery_cost
    Стоимость доставки данного товара в своем регионе.
    Необязательный элемент.

    name
    Название товарного предложения. В названии упрощенного предложения рекомендуется указывать наименование и код производителя.
    Обязательный элемент.

    vendor
    Производитель. Не отображается в названии предложения.
    Необязательный элемент.

    vendorCode
    Код товара (указывается код производителя). Не отображается в названии предложения.
    Необязательный элемент.

    description
    Описание товарного предложения. Длина текста не более 175 символов (не включая знаки препинания), запрещено использовать HTML-теги (информация внутри тегов публиковаться не будет).
    Необязательный элемент.

    sales_notes
    Элемент используется для отражения информации о минимальной сумме заказа, минимальной партии товара или необходимости предоплаты, а так же для описания акций, скидок и распродаж. Допустимая длина текста в элементе — 50 символов.
    Необязательный элемент.

    manufacturer_warranty
    Элемент предназначен для отметки товаров, имеющих официальную гарантию производителя.
    Необязательный элемент.
    Возможные значения:
    1) false — товар не имеет официальной гарантии;
    2) true — товар имеет официальную гарантию.

    country_of_origin
    Элемент предназначен для указания страны производства товара. Список стран, которые могут быть указаны в этом элементе, доступен по адресу: http://partner.market.yandex.ru/pages/help/Countries.pdf.
    Примечание. Если вы хотите участвовать в программе «Заказ на Маркете», то желательно указывать данный элемент в YML-файле.
    Необязательный элемент.

    adult
    Элемент обязателен для обозначения товара, имеющего отношение к удовлетворению сексуальных потребностей, либо иным образом эксплуатирующего интерес к сексу.
    Необязательный элемент.

    age
    Возрастная категория товара. Годы задаются с помощью атрибута unit со значением year, месяцы — с помощью атрибута unit со значением month.
    Допустимые значения параметра при unit="year": 0, 6, 12, 16, 18. Допустимые значения параметра при unit="month": 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12.
    Необязательный элемент.

    barcode
    Штрихкод товара, указанный производителем.
    Необязательный элемент. Элемент <offer> может содержать несколько элементов <barcode>.

    cpa
    Элемент предназначен для управления участием товарных предложений в программе «Заказ на Маркете».
    Необязательный элемент.

    param
    Элемент предназначен для указания характеристик товара. Для описания каждого параметра используется отдельный элемент <param>.
    Необязательный элемент. Элемент <offer> может содержать несколько элементов <param>.
    """

    def __init__(self):
        self.id = 0
        self.url = None
        self.price = None
        self.oldprice = None
        self.currencyId = None
        self.categoryId = None
        self.market_category = None
        self.pictures = []
        '''
        Добавление изображений pictures_append(picture)
        '''
        self.store = False
        self.pickup = False
        self.delivery = False
        self.local_delivery_cost = None
        self.name = None
        self.vendor = None
        self.vendorCode = None
        self.description = None
        self.sales_notes = None
        self.manufacturer_warranty = None
        self.country_of_origin = None
        self.adult = None
        self.age = None
        self.age_unit = None
        self.barcode = None
        self.cpa = None
        self.params = []
        '''
        Добавление изображений params_append(picture)
        '''

    def pictures_append(self, url):
        self.pictures.append(url)

    def params_append(self, param_name, param_value):
        self.params.append({'name': param_name, 'value': param_value})

    def validate(self):
        if self.price is None or self.currencyId is None or self.categoryId is None or self.name is None:
            # Not valid offer
            raise Exception(u"Поля price, currencyId, categoryId, name обязательны")