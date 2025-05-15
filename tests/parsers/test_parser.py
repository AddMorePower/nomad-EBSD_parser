import logging

from nomad.datamodel import EntryArchive

from nomad_ebsd_parser.parsers.parser import NewParser


def test_parse_file():
    parser = NewParser()
    archive = EntryArchive()
    parser.parse(
        'tests/data/Cu2160-2000_Site_1_Map_Data_9.cpr', archive, logging.getLogger()
    )

    assert archive.data.format_version == '5.0'
