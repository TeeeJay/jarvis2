#!/usr/bin/env python

import requests
from datetime import datetime, timedelta
from jobs import AbstractJob
from lxml import etree


class Yr(AbstractJob):

    def __init__(self, conf):
        self.url = conf['url']
        self.interval = conf['interval']
        self.timeout = conf.get('timeout')

    def _parse_tree(self, tree, date=None):
        if date is None:
            tabular = tree.xpath('/weatherdata/forecast/tabular/time[1]').pop()
            data_root = tree.xpath(
                '/weatherdata/observations/weatherstation[1]').pop()
        else:
            date_xpath = ('/weatherdata/forecast/tabular/time[@period=2 and'
                          ' starts-with(@from, "{date}")]').format(
                date=date.strftime('%F'))
            tabular = tree.xpath(date_xpath).pop()
            data_root = tabular

        windSpeed = data_root.xpath('windSpeed').pop()
        return {
            'location': tree.xpath('/weatherdata/location/name').pop().text,
            'temperature': data_root.xpath('temperature').pop().get('value'),
            'description': tabular.xpath('symbol').pop().get('name'),
            'wind': {
                'speed': windSpeed.get('mps'),
                'description': windSpeed.get('name'),
                'direction': data_root.xpath('windDirection').pop().get('name')
            }
        }

    def _parse(self, xml):
        tree = etree.fromstring(xml)
        tomorrow = datetime.now().date() + timedelta(days=1)
        return {
            'today': self._parse_tree(tree),
            'tomorrow': self._parse_tree(tree, tomorrow)
        }

    def get(self):
        r = requests.get(self.url, timeout=self.timeout)

        if r.status_code == 200 and len(r.content) > 0:
            return self._parse(r.content)
        return {}
