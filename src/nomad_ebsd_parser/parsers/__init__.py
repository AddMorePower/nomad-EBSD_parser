from nomad.config.models.plugins import ParserEntryPoint


class NewParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_ebsd_parser.parsers.parser import NewParser

        return NewParser(**self.dict())


parser_entry_point = NewParserEntryPoint(
    name='EBSDParser',
    description='EBSD parser entry point configuration.',
    mainfile_name_re='.*\.(cpr|h5oina)',
)
