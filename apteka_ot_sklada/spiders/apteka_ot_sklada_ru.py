import datetime
import math
import re

import scrapy
from scrapy import Request
from unicodedata import normalize
from w3lib.html import remove_tags, replace_escape_chars

from apteka_ot_sklada.items import Product


class AptekaOtSkladaRuSpider(scrapy.Spider):
    name = "apteka_ot_sklada_ru"
    allowed_domains = ["apteka-ot-sklada.ru"]
    start_urls = [
        'https://apteka-ot-sklada.ru/catalog/kosmetika%2Fbannye-serii%2Fgel-dlya-dusha',
        'https://apteka-ot-sklada.ru/catalog/tovary-dlya-mamy-i-malysha/gigiena-malysha/podguzniki-detskie',
        'https://apteka-ot-sklada.ru/catalog/sredstva-gigieny/mylo/mylo-zhidkoe',
    ]
    cookies = {'city': 92}

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse_product_urls)

    def parse_product_urls(self, response):
        urls = response.xpath('//a[@class="goods-card__link"]/@href').getall()
        for i in urls:
            url = response.urljoin(i)
            yield response.follow(url=url, callback=self.parse, cookies=self.cookies)
        next_page = response.xpath(
            '//div[@class="ui-pagination text text_weight_medium goods-catalog-view__pagination"]/ul/li[@class="ui-pagination__item ui-pagination__item_next"]/a/@href').get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse_product_urls, cookies=self.cookies)

    def parse(self, response):
        item = Product()
        item['timestamp'] = int(datetime.datetime.now().timestamp())
        rpc = response.xpath('//section[@class="container content-section-large"]/div[1]/@data-product-id').get()
        item['RPC'] = rpc
        item['url'] = response.url
        item['title'] = response.xpath('//h1[contains(@class,"text")]//text()').get()
        marketing_tags = response.xpath(
            '//ul[@class="goods-tags__list goods-tags__list_direction_horizontal"]/li/span/text()').getall()
        item['marketing_tags'] = [i.replace('\n', '').rstrip().lstrip() for i in marketing_tags]
        item['brand'] = ''  # На сайте отсуствуют бренды
        section = response.xpath('//ul[@class="ui-breadcrumbs__list"]/li/a/span/span/text()').getall()
        item['section'] = section
        stock = response.xpath('//div[@class="goods-offer-panel__part"]/div[@class="goods-cart-form"]')
        if stock:
            price_1 = response.xpath('//div[@class="goods-offer-panel__price"]/span[1]/text()').get()
            if price_1:
                price_1 = float(re.sub(r'₽|\s', '', price_1).strip())
            price_2 = response.xpath('//div[@class="goods-offer-panel__price"]/span[2]/text()').get()
            if price_2:
                price_2 = float(re.sub(r'₽|\s', '', price_2).strip())
            if price_1 and price_2 and price_2 > price_1:
                sale_tag = (price_1 / price_2) * 100
                item['price_data'] = {'current': price_1,
                                      'original': price_2,
                                      'sale_tag:': 'Скидка ' + str(math.ceil(sale_tag)) + '%'}
                item['stock'] = True
            else:
                item['price_data'] = {'current': price_1,
                                      'original': price_1, 'sale_tage': None}
                item['stock'] = True
        else:
            item['stock'] = False
            item['price_data'] = {'current': '0.0', 'original': '0.0', 'sale_tage': None}

        images_urls = response.xpath(
            '//div[@class="goods-gallery__sidebar"]/ul[@class="goods-gallery__preview-list"]/li/div/img/@src').getall()
        images = [response.urljoin(i) for i in images_urls if i]
        item['assets'] = {'video': [], 'view360': [], 'main_image': images[0], 'set_images': images}

        try:
            description_all = response.xpath('//section[@id="description"]').get()
            description_clear = remove_tags(description_all)
            description_clear = replace_escape_chars(description_clear, which_ones=('\t', '\r')).replace('\n', ' ')
            description_clear = normalize('NFKD', description_clear).strip()
            composition = re.findall('(?<=Состав).*?(?=Фармакологическое действие|Особенности '
                                     'продажи|Показания|Лекарственная форма|Способ применения и '
                                     'дозы|Противопоказания|\Z)', description_clear)
            composition = [x for x in composition if x != ' ']
            description = re.findall('(?<=Описание).*?(?=Фармакологическое действие|Особенности '
                                     'продажи|Показания|Лекарственная форма|Способ применения и '
                                     'дозы|Противопоказания|\Z)', description_clear)
            description = [x for x in description if x != ' ']
            pharma_effect = re.findall('(?<=Фармакологическое действие).*?(?=Описание|Особенности '
                                       'продажи|Показания|Лекарственная форма|Способ применения и '
                                       'дозы|Противопоказания|\Z)', description_clear)
            pharma_effect = [x for x in pharma_effect if x != ' ']
            indications = re.findall('(?<=Показания).*?(?=Описание|Особенности продажи|Показания|Лекарственная '
                                     'форма|Фармакологическое действие|Способ применения и '
                                     'дозы|Противопоказания|\Z)', description_clear)
            indications = [x for x in indications if x != ' ']
            contraindications = re.findall('(?<=Противопоказания).*?(?=Описание|Особенности '
                                           'продажи|Показания|Лекарственная форма|Фармакологическое действие|Способ '
                                           'применения и дозы|\Z)', description_clear)
            contraindications = [x for x in contraindications if x != ' ']
            dosage = re.findall('(?<=Способ применения и дозы).*?(?=Описание|Особенности '
                                'продажи|Показания|Лекарственная форма|Фармакологическое '
                                'действие|Противопоказания|\Z)', description_clear)
            dosage = [x for x in dosage if x != ' ']
            item['metadata'] = {'description': description[0] if description else '',
                                'СОСТАВ': composition[0] if composition else '',
                                'ФАРМАКОЛОГИЧЕСКОЕ ДЕЙСТВИЕ': pharma_effect[0] if pharma_effect else '',
                                'ПОКАЗАНИЯ': indications[0] if indications else '',
                                'ПРОТИВОПОКАЗАНИЯ': contraindications[0] if contraindications else '',
                                'СПОСОБ ПРИМЕНЕНИЯ И ДОЗЫ': dosage[0] if dosage else ''
                                }
        except TypeError:
            item['metadata'] = {'description': '',
                                'СОСТАВ': '',
                                'ФАРМАКОЛОГИЧЕСКОЕ ДЕЙСТВИЕ': '',
                                'ПОКАЗАНИЯ': '',
                                'ПРОТИВОПОКАЗАНИЯ': '',
                                'СПОСОБ ПРИМЕНЕНИЯ И ДОЗЫ': ''
                                }
        item['variants'] = 1  # На сайте отсуствуют вариативные товары
        yield item
