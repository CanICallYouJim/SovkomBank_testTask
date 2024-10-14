import gzip
import xml.etree.ElementTree as ET
from databases.models import *
from databases.queries.orm import SyncORM


class ParseXML:
    file_path = "ExtrajudicialData.xml.gz"

    def __init__(self):
        self._root = self.parse_xml(self.decompress_gz_file())

    @classmethod
    def decompress_gz_file(cls):
        with gzip.open(cls.file_path, 'rb') as f_in:
            return f_in.read()

    @staticmethod
    def parse_xml(xml_data):
        root_xml = ET.fromstring(xml_data)
        return root_xml

    def messages_generator(self):
        """
        Генератор, который возвращает по одному элементу ExtrajudicialBankruptcyMessage.
        """
        for message in self._root.findall('.//ExtrajudicialBankruptcyMessage'):
            yield self._extract_data_from_xml(message)

    @staticmethod
    def _add_pk_id(data, key, value):
        for v in data.values():
            if isinstance(v, dict):
                # Если значение - словарь, добавляем ключ-значение
                v[key] = value
            elif isinstance(v, list):
                # Если значение - список, проходим по каждому элементу
                for item in v:
                    item[key] = value
        return data

    def _extract_data_from_xml(self, message):

        bankruptcy_message_data = {
            'id': message.find('Id').text,
            'number': message.find('Number').text,
            'type': message.find('Type').text,
            'publish_date': message.find('PublishDate').text,
            'finish_reason': message.find('FinishReason').text if message.find('FinishReason') is not None else None
        }

        debtor = message.find('Debtor')
        debtor_data = {
            'name': debtor.find('Name').text,
            'birth_date': debtor.find('BirthDate').text,
            'birth_place': debtor.find('BirthPlace').text,
            'address': debtor.find('Address').text,
            'inn': debtor.find('Inn').text if debtor.find('Inn') is not None else None
        }

        # Извлечение информации о банках
        banks = []
        for bank in message.findall('.//Bank'):
            banks.append({
                'name': bank.find('Name').text,
                'bik': bank.find('Bik').text if bank.find('Bik') is not None else None
            })

        # Извлечение обязательств
        obligations = []
        for obligation in message.findall('.//MonetaryObligation'):
            obligations.append({
                'creditor_name': obligation.find('CreditorName').text,
                'content': obligation.find('Content').text,
                'basis': obligation.find('Basis').text,
                'total_sum': obligation.find('TotalSum').text,
                'debt_sum': obligation.find('DebtSum').text if obligation.find('DebtSum')  is not None else None
            })

        # Извлечение обязательных платежей
        payments = []
        for payment in message.findall('.//ObligatoryPayment'):
            payments.append({
                'name': payment.find('Name').text,
                'sum': payment.find('Sum').text
            })

        publisher = message.find('Publisher')
        publisher_data = {
            'name': publisher.find('Name').text,
            'inn': publisher.find('Inn').text,
            'ogrn': publisher.find('Ogrn').text
        }

        result = {'bankruptcy_message': bankruptcy_message_data}
        d = self._add_pk_id(data={
            'publisher': publisher_data,
            'debtor': debtor_data,
            'banks': banks,
            'obligations': obligations,
            'payments': payments
        }, key='extra_judicial_bankruptcy_message', value=message.find('Id').text,
        )

        result.update(d)

        return result

    @staticmethod
    def parse_to_database():
        for message in ParseXML().messages_generator():
            key_model = {'bankruptcy_message': ExtrajudicialBankruptcyMessage, 'publisher': Publisher, 'debtor': Debtor,
                         'banks': Bank, 'obligations': MonetaryObligation, 'payments': ObligatoryPayment}

            for key, value in message.items():
                if isinstance(value, list):
                    instances = [key_model[key](**x) for x in value]
                else:
                    instances = [key_model[key](**value)]

                SyncORM.add_to_model(instances=instances)
