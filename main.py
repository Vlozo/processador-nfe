import xml.etree.ElementTree as ET
import system
from clients import Client
import os
import logging

logging.basicConfig(filename="app.log", level=logging.INFO)

def set_clients(clients):
    cts = []
    for c in clients:
        cts.append(Client(c))
    return cts

def is_client(id, clients_list):
    ct = clients_list.get(id)
    if ct:
        return ct
    return False

def check_cfop(cfop_list):
    normalized = [(s[0], s[1:]) for s in cfop_list]
    protocol = normalized[0]

    if protocol[1] in ["202", "411", "556"]:
        return "r"
    if protocol[0] in ["1", "2", "3"]:
        return "p"
    elif protocol[0] in ["5", "6", "7"]:
        return "s"
    else:
        return "e"
    
def set_data(ct_op: Client, period, value):
    if period not in ct_op:
        ct_op[period] = []

    ct_op[period].append(value)

def read_NFe(path, clients):
    try:
        tree = ET.parse(path)
        root = tree.getroot()

        ns = {"nfe": "http://www.portalfiscal.inf.br/nfe"}
        emit = root.find(".//nfe:emit", ns)
        dest = root.find(".//nfe:dest", ns)

        dh_emi = root.find(".//nfe:ide/nfe:dhEmi", ns).text
        period = dh_emi[:7]

        emit_id = emit.find("nfe:CNPJ", ns).text
        dest_id = dest.find("nfe:CPF", ns)

        if dest_id is not None:
            dest_id = dest_id.text
        else:
            dest_id = dest.find("nfe:CNPJ", ns).text

        emit_ct = is_client(emit_id, clients)
        dest_ct = is_client(dest_id, clients)

        cfops = []
        for det in root.findall(".//nfe:det", ns):
            # A provisional lazy solution to avoid unnecessary O(n) complexity
            if len(cfops) >= 2: 
                break
            prod = det.find("nfe:prod", ns) 
            if prod is not None: 
                cfop = prod.find("nfe:CFOP", ns)
                cfops.append(cfop.text)
        
        vNF = root.find(".//nfe:vNF", ns).text
        vNF = float(vNF)

        match check_cfop(cfops):
            case "s":
                if emit_ct:
                    set_data(emit_ct.sales, period, vNF)
                if dest_ct:
                    set_data(dest_ct.purcharses, period, vNF)
            case "p":
                if dest_ct:
                    set_data(dest_ct.purcharses, period, vNF)
                if emit_ct:
                    set_data(emit_ct.sales, period, vNF)
            case "r":
                set_data(emit_ct.returns, period, vNF)
            case _:
                logging.info("Houve um erro ao computar o protocolo de CFOP.")

    except FileNotFoundError:
        logging.info("Arquivo XML não encontrado.")
    except Exception as e:
        logging.info(f"Ocorreu um erro ao ler o XML: {e}")

def br_format(value: float) -> str:
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

output_dir = "resumos" 

def save(ct: Client):
    results = ct.sum_all()
    try:
        os.makedirs(output_dir, exist_ok=True)

        for period, values in results.items():
            ts, tr, tp, base = values

            filename = os.path.join(output_dir, f"resumo_{ct.cnpj}({period}).txt")

            with open(filename, 'w', encoding='utf-8') as file:
                file.write(
                    f"\nCliente: {ct.cnpj}\nCompetência: {period}\n\n"
                    f"Total Vendas.......: R$ {br_format(ts)}\n"
                    f"Total Devoluções...: R$ {br_format(tr)}\n"
                    f"Total Compras......: R$ {br_format(tp)}\n\n"
                    f"BASE DO SIMPLES (Vendas - Devoluções):\nR$ {br_format(base)}"
                )
            logging.info(f"Arquivo {filename} atualizado.")
    except IOError as e:
        logging.info(f"Erro ao criar o arquivo: {e}")

def main(path, is_recursive):
    if not path or path == "()":
        return "Nenhum diretório foi selecionado"
    
    my_clients = system.read_clients()
    ct_dict = {c.cnpj: c for c in set_clients(my_clients)}

    files = system.get_all_xml_from(path, is_recursive)
    for i in files:
        read_NFe(i, ct_dict)

    for c in ct_dict.values():
        save(c)
    
    return f"Notas processadas, verifique os arquivos no diretório \"{output_dir}\"."

if __name__ == "__main__":
    main()