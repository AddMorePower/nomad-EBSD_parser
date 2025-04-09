# from typing import (
#     TYPE_CHECKING,
# )

# if TYPE_CHECKING:
#     from nomad.datamodel.datamodel import (
#         EntryArchive,
#     )
#     from structlog.stdlib import (
#         BoundLogger,
#     )

from nomad.config import config
from nomad.datamodel.data import Schema
from nomad.metainfo import Quantity, SchemaPackage, MSection, Datetime, SubSection

configuration = config.get_plugin_entry_point(
    'nomad_ebsd_parser.schema_packages:schema_package_entry_point'
)

m_package = SchemaPackage()


class Job(MSection):
    magnification = Quantity(type=float, shape=[])
    beam_voltage = Quantity(type=float, shape=[])
    nb_points = Quantity(type=int, shape=[])
    tilt_angle = Quantity(type=float, shape=[])
    tilt_axis = Quantity(type=float, shape=[])
    x_cells = Quantity(type=int, shape=[])
    y_cells = Quantity(type=int, shape=[])


class SEMFields(MSection):
    detector_orientation_euler = Quantity(type=float, shape=[3])


class StagePosition(MSection):
    x_axis = Quantity(type=float, shape=[])
    y_axis = Quantity(type=float, shape=[])
    z_axis = Quantity(type=float, shape=[])
    rotation = Quantity(type=float, shape=[])
    tilt = Quantity(type=float, shape=[])


class AcquisitionSurface(MSection):
    surface_orientation_euler = Quantity(type=float, shape=[3])


class Phase(MSection):
    structure_name = Quantity(type=str)
    reference = Quantity(type=str)
    lattice_dimensions = Quantity(type=float, shape=[3])
    lattice_angles = Quantity(type=float, shape=[3])
    laue_group = Quantity(type=int, shape=[])
    space_group = Quantity(type=int, shape=[])
    nb_reflectors = Quantity(type=int, shape=[])


class EBSDOutput(Schema):
    version = Quantity(type=str)
    date = Quantity(type=Datetime)
    description = Quantity(type=str)
    notes = Quantity(type=str)
    project_notes = Quantity(type=str)

    job = SubSection(sub_section=Job.m_def, repeats=False)
    sem_fileds = SubSection(sub_section=SEMFields.m_def, repeats=False)
    stage_position = SubSection(sub_section=StagePosition.m_def, repeats=False)
    acquisition_surface = SubSection(sub_section=AcquisitionSurface.m_def, repeats=False)
    phases = SubSection(sub_section=Phase.m_def, repeats=True)



m_package.__init_metainfo__()
