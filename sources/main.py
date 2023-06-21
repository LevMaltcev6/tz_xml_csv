import os
import random
import string
import zipfile
import xml.etree.ElementTree as ET
import csv
from typing import Tuple, List, Dict, ClassVar


class Config:
    id_level_csv_name: ClassVar[str] = 'id_level.csv'
    id_object_csv_name: ClassVar[str] = 'id_object.csv'


class XMLFileGenerator:
    def __init__(self, directory_to_store_files: str):
        self.directory = directory_to_store_files

    @staticmethod
    def generate_random_string(length: int = 10) -> str:
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

    def create_xml_structure(self) -> ET.Element:
        root = ET.Element("root")
        ET.SubElement(root, "var", {"name": "id", "value": self.generate_random_string()})
        ET.SubElement(root, "var", {"name": "level", "value": str(random.randint(1, 100))})
        objects = ET.SubElement(root, "objects")
        for _ in range(random.randint(1, 10)):
            ET.SubElement(objects, "object", {"name": self.generate_random_string()})
        return root

    def generate_zip_archive_with_xml_files(self, archive_index: int) -> None:
        with zipfile.ZipFile(os.path.join(self.directory, f"archive_{archive_index}.zip"), "w") as zf:
            for i in range(100):
                xml_file = self.create_xml_structure()
                zf.writestr(f"file_{i}.xml", ET.tostring(xml_file, encoding="unicode"))


class XMLFileProcessor:
    def __init__(self, directory_with_zip_archives: str):
        self.directory = directory_with_zip_archives

    @staticmethod
    def extract_data_from_xml(xml_content: str) -> Tuple[Dict[str, str], List[str]]:
        tree = ET.fromstring(xml_content)
        id_value = tree.find("./var[@name='id']").get("value")
        level_value = tree.find("./var[@name='level']").get("value")
        object_names = [obj.get("name") for obj in tree.findall("./objects/object")]
        return {"id": id_value, "level": level_value}, object_names

    def process_single_zip_archive(self, archive_filename: str) -> None:
        with zipfile.ZipFile(os.path.join(self.directory, archive_filename), "r") as zf:
            for file in zf.namelist():
                xml_content = zf.read(file).decode("utf-8")
                id_level, object_names = self.extract_data_from_xml(xml_content)
                self.write_data_to_csv(Config.id_level_csv_name, id_level)
                for object_name in object_names:
                    self.write_data_to_csv(Config.id_object_csv_name, {"id": id_level["id"], "object_name": object_name})

    @staticmethod
    def write_data_to_csv(filename: str, data: Dict[str, str]) -> None:
        with open(filename, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data.keys())
            writer.writerow(data)

    def process_all_zip_archives_in_directory(self) -> None:
        for filename in os.listdir(self.directory):
            if filename.endswith(".zip"):
                self.process_single_zip_archive(filename)


def main():
    xml_generator = XMLFileGenerator("./archives")
    for i in range(50):
        xml_generator.generate_zip_archive_with_xml_files(i)

    xml_processor = XMLFileProcessor("./archives")
    xml_processor.process_all_zip_archives_in_directory()


if __name__ == "__main__":
    main()
