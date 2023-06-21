import os
import time
import xml.etree.ElementTree as ET

import pytest

from sources.main import XMLFileGenerator, XMLFileProcessor, main as run_main


@pytest.fixture
def archives_path() -> str:
    return "./archives"


@pytest.fixture()
def clear_files(archives_path):
    yield
    zip_files = [file for file in os.listdir(archives_path) if file.endswith('.zip')]
    for file in zip_files:
        os.remove(os.path.join(archives_path, file))

    os.remove("id_level.csv")
    os.remove("id_object.csv")


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


def test_generate_and_process_zip_archive(archives_path, clear_files):
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


def test_generate_multiple_zip_archives(archives_path):
    os.makedirs(archives_path, exist_ok=True)

    run_main()

    zip_files = [file for file in os.listdir(archives_path) if file.endswith('.zip')]
    assert len(zip_files) == 50

    for file in zip_files:
        os.remove(os.path.join(archives_path, file))


def test_multiprocessing_file_generator_performance(archives_path, clear_files):
    generator = XMLFileGenerator("archives")
    start_time = time.time()
    generator.generate_multiple_zip_archives(150)
    end_time = time.time()
    multiprocessing_time = end_time - start_time

    zip_files = [file for file in os.listdir(archives_path) if file.endswith('.zip')]
    for file in zip_files:
        os.remove(os.path.join(archives_path, file))

    start_time = time.time()
    for i in range(300):
        generator.generate_zip_archive_with_xml_files(i)
    end_time = time.time()

    single_process_time = end_time - start_time

    assert single_process_time > multiprocessing_time


def test_multiprocessing_file_processor_performance(clear_files, archives_path):
    generator = XMLFileGenerator("archives")
    generator.generate_multiple_zip_archives(100)

    processor = XMLFileProcessor("archives")

    start_time = time.time()
    processor.process_all_zip_archives_in_directory()
    end_time = time.time()
    multiprocessing_time = end_time - start_time

    start_time = time.time()
    for filename in os.listdir(archives_path):
        if filename.endswith(".zip"):
            processor.process_single_zip_archive(filename)
    end_time = time.time()
    single_core_time = end_time - start_time

    assert single_core_time > multiprocessing_time
