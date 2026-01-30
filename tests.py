from main import check_cfop, is_client, set_clients, set_data, read_NFe
from clients import Client
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

xml_data = """
    <NFe xmlns="http://www.portalfiscal.inf.br/nfe">
        <infNFe versao="4.00" Id="NFe12345678901234567890123456789012345678901234">
            <ide>
                <dhEmi>2025-12-22T11:33:22-03:00</dhEmi>
            </ide>
            <emit>
                <CNPJ>12345678000199</CNPJ>
            </emit>
            <dest>
                <CPF>12345678901</CPF>
            </dest>
            <det nItem="1">
                <prod>
                    <CFOP>5102</CFOP>
                </prod>
            </det>
            <total>
                <ICMSTot>
                    <vNF>500.00</vNF>
                </ICMSTot>
            </total>
        </infNFe>
    </NFe>
"""

class TestCheckCFOP(unittest.TestCase):

    def test_protocol_r(self):
        self.assertEqual(check_cfop(["1202"]), "r")
        self.assertEqual(check_cfop(["2411"]), "r")
        self.assertEqual(check_cfop(["3556"]), "r")

    def test_protocol_p(self):
        self.assertEqual(check_cfop(["1999"]), "p")
        self.assertEqual(check_cfop(["2111"]), "p")
        self.assertEqual(check_cfop(["3123"]), "p")

    def test_protocol_s(self):
        self.assertEqual(check_cfop(["5999"]), "s")
        self.assertEqual(check_cfop(["6555"]), "s")
        self.assertEqual(check_cfop(["7123"]), "s")

    def test_protocol_e(self):
        self.assertEqual(check_cfop(["8999"]), "e")
        self.assertEqual(check_cfop(["4000"]), "e")

    def test_multiple_cfops(self):
        # The function only looks at the first element of the list.
        self.assertEqual(check_cfop(["1202", "5999", "8999"]), "r")
        self.assertEqual(check_cfop(["2111", "5999"]), "p")

class TestClientRelationedMethods(unittest.TestCase):

    def test_set_clients(self):
        result = set_clients(["12345678900", "12345678901", "12345678902"])
        expected = [ Client("12345678900"), Client("12345678901"), Client("12345678902") ]
        self.assertEqual(result, expected)
    
    def test_is_client(self):
        input = ["12345678900"]
        my_dict = {c.cnpj: c for c in set_clients(input)}
        expected = Client(input[0])
        result = is_client(input[0], my_dict)
        self.assertEqual(result, expected)
    
    def test_is_not_client(self):
        input = ["12345678900"]
        my_dict = {c.cnpj: c for c in set_clients(input)}
        result = is_client("98765432100", my_dict)
        self.assertEqual(result, False)
    
    def test_set_data(self):
        ct = Client("12345678900")
        set_data(ct.sales, "2025-12", float(120.90))
        set_data(ct.purcharses, "2025-12", float(210.50))
        set_data(ct.returns, "2025-12", float(350.60))
        result = [ct.sales.get("2025-12"), ct.purcharses.get("2025-12"), ct.returns.get("2025-12")]
        expected = [[120.90], [210.50], [350.60]]
        self.assertEqual(result, expected)
    
    def test_multiple_periods_set_data(self):
        ct = Client("12345678900")
        set_data(ct.purcharses, "2026-01", float(50.90))
        set_data(ct.purcharses, "2026-01", float(30.50))
        set_data(ct.purcharses, "2026-02", float(20.40))
        set_data(ct.purcharses, "2026-03", float(75.50))
        result = [ct.purcharses.get("2026-01"), ct.purcharses.get("2026-02"), ct.purcharses.get("2026-03")]
        expected = [[50.90, 30.50], [20.40], [75.50]]
        self.assertEqual(result, expected)
    
    def test_client_final_sum(self):
        ct = Client("12345678900")

        set_data(ct.purcharses, "2026-01", float(50.00))
        set_data(ct.purcharses, "2026-01", float(100.00))

        set_data(ct.sales, "2026-01", float(150.00))
        set_data(ct.sales, "2026-01", float(90.00))
        set_data(ct.sales, "2026-02", float(40.00))
        set_data(ct.sales, "2026-02", float(30.00))

        set_data(ct.returns, "2026-01", float(50.00))
        set_data(ct.returns, "2026-02", float(15.00))
        set_data(ct.returns, "2026-02", float(30.00))

        expected = {"2026-01":[240.00, 50.00, 150.00, 190.00], "2026-02":[70.00, 45.00, 0, 25.00]}
        self.assertEqual(ct.sum_all(), expected)

class TestNfeReading(unittest.TestCase):

    def test_nfe_processing(self):
        clients = {"12345678000199" : Client("12345678000199")}
        fake_tree = ET.ElementTree(ET.fromstring(xml_data))
        with patch("xml.etree.ElementTree.parse", return_value=fake_tree):
            read_NFe("fake.xml", clients)
            self.assertEqual(clients.get("12345678000199").sales, {"2025-12":[float(500.0)]})
    
    def test_nfe_cross_clients_processing(self):
        clients = {"12345678901" : Client("12345678901"), "12345678000199" : Client("12345678000199")}
        fake_tree = ET.ElementTree(ET.fromstring(xml_data))
        with patch("xml.etree.ElementTree.parse", return_value=fake_tree):
            read_NFe("fake.xml", clients)
            self.assertEqual(clients.get("12345678000199").sales, clients.get("12345678901").purcharses)

if __name__ == "__main__":
    unittest.main()