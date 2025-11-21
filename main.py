import xml.etree.ElementTree as ET
import zipfile
from zipfile import ZipFile
f = "C:\Balthazaar\RDD_80.005.09390_097.zip"
with ZipFile(f, "r") as zip:
    zip.printdir()
    zip.extractall()