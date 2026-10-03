import unittest
from unittest.mock import MagicMock, patch
from database import describe_columns, fetch_field_groups, fetch_records_by_group
import app

class QueryColumnTests(unittest.TestCase):
    def test_alias_order_types_and_filters(self):
        fields=describe_columns([('Emp Name','DB_TYPE_VARCHAR'),('Amount','DB_TYPE_NUMBER'),('Created','DB_TYPE_DATE')], 'Case Details')
        app.configure_fields({'Case Details':fields,'Claim Details':[]})
        self.assertEqual(app._result_headers(app.CASE_RESULT_FIELDS),['Emp Name','Amount','Created'])
        self.assertEqual([kind for _,_,kind in fields],['text','number','date'])
        self.assertTrue(app.matches({'Case Details::Amount':12},'Case Details::Amount','Greater than',10))

    def test_duplicate_alias_rejected(self):
        with self.assertRaisesRegex(ValueError,'duplicate SELECT alias'):
            describe_columns([('Name','VARCHAR'),('Name','VARCHAR')],'Case Details')

    def test_empty_query_keeps_metadata(self):
        conn=MagicMock()
        cursor=conn.__enter__.return_value.cursor.return_value.__enter__.return_value
        cursor.description=[('Emp Name','DB_TYPE_VARCHAR')]
        cursor.fetchmany.return_value=[]
        with patch('database.get_settings',return_value={}), patch('database.build_query',return_value='SELECT name FROM employee'), patch('database.connect_db',return_value=conn):
            groups=fetch_field_groups()
            self.assertEqual(groups['Case Details'][0][1],'Emp Name')
            self.assertEqual(fetch_records_by_group()['Case Details'],[])

if __name__=='__main__':
    unittest.main()
