import os, sys, tempfile, unittest
os.environ.setdefault('APP_ENV','test')
os.environ.setdefault('DATABASE_URL', os.path.join(tempfile.gettempdir(),'investedge-test-suite.db'))
os.environ.setdefault('USE_SIMULATOR','false')
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import main

class CoreTests(unittest.TestCase):
    def test_password_hash_verifies_and_salts(self):
        a=main.pw_hash('CorrectHorseBattery9!')
        b=main.pw_hash('CorrectHorseBattery9!')
        self.assertNotEqual(a,b)
        self.assertTrue(main.pw_ok('CorrectHorseBattery9!',a))
        self.assertFalse(main.pw_ok('wrong',a))
    def test_token_round_trip(self):
        token=main.token_for(123)
        self.assertEqual(main.user_id_from_token(token),123)
    def test_normalize_symbol(self):
        self.assertEqual(main.normalize_symbol(' hdfc bank '),'HDFCBANK')
    def test_unknown_symbol_is_not_fabricated(self):
        from fastapi.testclient import TestClient
        c=TestClient(main.app)
        self.assertEqual(c.get('/api/signal/NOTAREALSTOCK').status_code,404)
    def test_signal_ranges(self):
        s=main.signal_for(100,2.0)
        self.assertIn(s['signal'],('BUY','HOLD','SELL'))
        self.assertGreaterEqual(s['confidence'],0)
        self.assertLessEqual(s['confidence'],100)

if __name__=='__main__': unittest.main(verbosity=2)
