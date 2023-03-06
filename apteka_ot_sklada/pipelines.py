# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import re

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class AptekaOtSkladaPipeline:
    def process_item(self, item, spider):
        if item['metadata']['СОСТАВ'] == '':
            item['metadata'].pop('СОСТАВ')
        else:
            item['metadata']['СОСТАВ'].rstrip().lstrip()
        if item['metadata']['ФАРМАКОЛОГИЧЕСКОЕ ДЕЙСТВИЕ'] == '':
            item['metadata'].pop('ФАРМАКОЛОГИЧЕСКОЕ ДЕЙСТВИЕ')
        if item['metadata']['ПОКАЗАНИЯ'] == '':
            item['metadata'].pop('ПОКАЗАНИЯ')
        if item['metadata']['ПРОТИВОПОКАЗАНИЯ'] == '':
            item['metadata'].pop('ПРОТИВОПОКАЗАНИЯ')
        if item['metadata']['СПОСОБ ПРИМЕНЕНИЯ И ДОЗЫ'] == '':
            item['metadata'].pop('СПОСОБ ПРИМЕНЕНИЯ И ДОЗЫ')
        for sec in item['section']:
            if sec == "Главная":
                item['section'].remove(sec)
        clear_description = item['metadata']['description']
        item['metadata']['description'] = re.sub('\s{2,}','', clear_description)


        return item
