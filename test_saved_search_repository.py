import unittest
from unittest.mock import MagicMock, patch
import saved_search_repository as repo

class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.search={'name':'OPEN_CASES','match_mode':'Match all (AND)','criteria':[{'field':'Case Details::Case Number','operator':'Equals','value':'100'}]}
        self.conn=MagicMock()
        self.cursor=self.conn.__enter__.return_value.cursor.return_value.__enter__.return_value
        self.settings=patch.object(repo,'get_settings',return_value={'schema':'PIC_MASTER1'})
        self.connect=patch.object(repo,'connect_db',return_value=self.conn)
        self.settings.start();self.connect.start()
        self.addCleanup(self.settings.stop);self.addCleanup(self.connect.stop)

    def test_save_commits_and_reload_reads_database(self):
        driver=MagicMock()
        with patch.dict('sys.modules',{'oracledb':driver}): repo.insert_saved_search(self.search)
        self.conn.__enter__.return_value.commit.assert_called_once()
        lob=MagicMock();lob.read.return_value='[{"field":"Case Details::Case Number","operator":"Equals","value":"100"}]'
        self.cursor.__iter__.return_value=iter([('OPEN_CASES','Match all (AND)',lob)])
        self.assertEqual(repo.load_saved_searches(),[self.search])

    def test_failure_rolls_back(self):
        self.cursor.execute.side_effect=RuntimeError('failed')
        with patch.dict('sys.modules',{'oracledb':MagicMock()}),self.assertRaises(RuntimeError):
            repo.insert_saved_search(self.search)
        self.conn.__enter__.return_value.rollback.assert_called_once()
        self.conn.__enter__.return_value.commit.assert_not_called()

    def test_delete_bound_and_committed(self):
        repo.remove_saved_search("NAME'X")
        self.assertEqual(self.cursor.execute.call_args.kwargs,{'name':"NAME'X"})
        self.conn.__enter__.return_value.commit.assert_called_once()

    def test_digest_ignores_criteria_order(self):
        other={'field':'Status','operator':'Equals','value':'Open'}
        a=dict(self.search,criteria=self.search['criteria']+[other])
        b=dict(a,criteria=list(reversed(a['criteria'])))
        self.assertEqual(repo.criteria_hash(a),repo.criteria_hash(b))
