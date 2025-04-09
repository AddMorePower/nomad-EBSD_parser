from nomad.config.models.plugins import SchemaPackageEntryPoint


class NewSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_ebsd_parser.schema_packages.schema_package import m_package

        return m_package


schema_package_entry_point = NewSchemaPackageEntryPoint(
    name='EBSDSchema',
    description='Schema for EBSD files within AddMorePower.',
)
