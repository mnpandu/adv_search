import unittest
from unittest.mock import patch
import app

class SavedSearchRestoreTests(unittest.TestCase):
    def test_load_and_run_restore_controls(self):
        app.configure_fields({'Case Details':[('Case Details::Case Number','Case Number','text')], 'Claim Details':[]})
        saved={'name':'My case','match_mode':'Match all (AND)','criteria':[{'field':'Case Details::Case Number','operator':'In','value':'100, 200'}]}
        for run in (False,True):
            state={}
            with patch.object(app.st,'session_state',state), patch.object(app,'_run_query') as query:
                (app._apply_and_run_saved_search if run else app._apply_saved_search)(saved)
                self.assertEqual(state['selected_fields::Case Details'],['Case Details::Case Number'])
                self.assertEqual(state['operator::Case Details::Case Number'],'In')
                self.assertEqual(state['value::Case Details::Case Number::In'],'100, 200')
                self.assertTrue(state['expand_field_groups'])
                self.assertEqual(query.call_count,int(run))
