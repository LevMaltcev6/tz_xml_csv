import os
import xml.etree.ElementTree as ET

import pytest

from sources.main import XMLFileGenerator, XMLFileProcessor, main as run_main


@pytest.fixture
def archives_path() -> str:
    return "./archives"


def test_generate_random_string(archives_path):
    generator = XMLFileGenerator(archives_path)
    random_str = generator.generate_random_string()
    assert len(random_str) == 10
    assert isinstance(random_str, str)


def test_create_xml_structure(archives_path):
    generator = XMLFileGenerator(archives_path)
    xml_file = generator.create_xml_structure()
    assert isinstance(xml_file, ET.Element)
    assert xml_file.tag == "root"
    assert len(xml_file.findall("./objects/object")) <= 10


def test_extract_data_from_xml(archives_path):
    processor = XMLFileProcessor(archives_path)
    xml_structure = ET.tostring(XMLFileGenerator(archives_path).create_xml_structure(), encoding="unicode")
    data, object_names = processor.extract_data_from_xml(xml_structure)
    assert isinstance(data, dict)
    assert "id" in data
    assert "level" in data
    assert isinstance(object_names, list)


def test_generate_and_process_zip_archive(archives_path):
    os.makedirs(archives_path, exist_ok=True)

    generator = XMLFileGenerator(archives_path)
    generator.generate_zip_archive_with_xml_files(0)

    processor = XMLFileProcessor(archives_path)
    processor.process_single_zip_archive("archive_0.zip")

    assert os.path.exists("id_level.csv")
    assert os.path.exists("id_object.csv")

    with open("id_level.csv", "r") as file:
        assert file.read() != ""
    with open("id_object.csv", "r") as file:
        assert file.read() != ""

    os.remove(os.path.join(archives_path, "archive_0.zip"))
    os.remove("id_level.csv")
    os.remove("id_object.csv")


def test_generate_multiple_zip_archives(archives_path):
    os.makedirs(archives_path, exist_ok=True)

    run_main()

    zip_files = [file for file in os.listdir(archives_path) if file.endswith('.zip')]
    assert len(zip_files) == 50

    for file in zip_files:
        os.remove(os.path.join(archives_path, file))
    os.remove("id_level.csv")
    os.remove("id_object.csv")
