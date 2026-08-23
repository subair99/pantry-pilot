import unittest
import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from tools.twilio_mcp import send_volunteer_sms
from tools.inventory_db import log_donation, get_pending_donations
from tools.ocr_mcp import extract_donation_details

class TestMCPTools(unittest.TestCase):

    def test_twilio_mock_fallback(self):
        os.environ.pop("TWILIO_ACCOUNT_SID", None)
        response = send_volunteer_sms(to_phone="+15550101", message="Test SMS")
        self.assertEqual(response["status"], "success")
        self.assertIn("MOCK", response["sid"])

    def test_inventory_db_log_and_fetch(self):
        result = log_donation(donor_name="Test Donor", items=["test item"], quantity=5, notes="Test notes")
        self.assertIn("Successfully logged", result)
        pending = get_pending_donations()
        self.assertIsInstance(pending, list)

    def test_ocr_extraction(self):
        raw_text = "Donating 10 boxes of cereal."
        result = extract_donation_details(raw_text)
        
        # The tool returns a JSON string. We just check if it contains the key.
        if isinstance(result, str):
            self.assertIn("items", result)
        else:
            self.assertIsInstance(result, dict)
            self.assertIn("items", result)

if __name__ == '__main__':
    unittest.main(verbosity=2)
