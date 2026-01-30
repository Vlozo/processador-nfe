import os
from os import listdir
from os.path import isfile, join
import glob
import csv

CSV_FILE = "clients.csv"

def read_clients():
    if not os.path.exists(CSV_FILE):
        return []
    with open(CSV_FILE, newline="") as f:
        reader = csv.reader(f)
        return [row[0] for row in reader]

def add_client(client_id):
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([client_id])

def remove_client(client_id):
    clients = read_clients()
    clients = [c for c in clients if c != client_id]
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        for c in clients:
            writer.writerow([c])

def get_files(path):
    return [f for f in listdir(path) if isfile(join(path, f))]

def get_all_xml_from(path, is_recursive: bool):
    if is_recursive:
        xml_files = glob.glob(os.path.join(path, "**", "*.xml"), recursive=True)
    else:
        xml_files = glob.glob(os.path.join(path, "*.xml"))
    return xml_files
