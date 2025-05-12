from typing import (
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

import logging
import os

import numpy as np
from nomad.config import config
from nomad.parsing.parser import MatchingParser

import nomad_ebsd_parser.schema_packages.schema_package as ebsd

configuration = config.get_plugin_entry_point(
    'nomad_ebsd_parser.parsers:parser_entry_point'
)


class NewParser(MatchingParser):
    def rad2deg(self, rad):
        return (rad * 180) / np.pi

    def parse_output(self):
        if self.extension == 'cpr':
            self.output_data.format_version = self.datafile['General']['Version']
            self.output_data.date = self.datafile['General']['Date']
            self.output_data.description = self.datafile['General']['Description']
            self.output_data.notes = self.datafile['General']['Notes']
            self.output_data.project_notes = self.datafile['General']['ProjectNotes']
        if self.extension == 'h5oina':
            self.output_data.format_version = self.datah5['Format Version'].asstr()[0]
            self.output_data.date = self.datafile['Acquisition Date'].asstr()[0]
            self.output_data.description = (
                self.datafile['Project Label'].asstr()[0]
                + self.datafile['Specimen Label'].asstr()[0]
            )
            self.output_data.notes = self.datafile['Specimen Notes'].asstr()[0]
            self.output_data.project_notes = self.datafile['Project Notes'].asstr()[0]

    def parse_job(self):
        job = self.output_data.m_create(ebsd.Job)
        if self.extension == 'cpr':
            job.magnification = float(self.datafile['Job']['Magnification'])
            job.beam_voltage = float(self.datafile['Job']['kV'])
            job.nb_points = int(self.datafile['Job']['NoOfPoints'])
            job.tilt_angle = float(self.datafile['Job']['TiltAngle'])
            job.tilt_axis = float(self.datafile['Job']['TiltAxis'])
            job.x_cells = int(self.datafile['Job']['xCells'])
            job.y_cells = int(self.datafile['Job']['yCells'])
        if self.extension == 'h5oina':
            job.magnification = self.datafile['Magnification'][()]
            job.beam_voltage = self.datafile['Beam Voltage'][()]
            job.nb_points = self.datafile['X Cells'][()] * self.datafile['Y Cells'][()]
            job.tilt_angle = self.rad2deg(self.datafile['Tilt Angle'][()])
            job.tilt_axis = self.rad2deg(self.datafile['Tilt Axis'][()])
            job.x_cells = self.datafile['X Cells'][()]
            job.y_cells = self.datafile['Y Cells'][()]

    def parse_semfields(self):
        sem_fields = self.output_data.m_create(ebsd.SEMFields)
        if self.extension == 'cpr':
            doeuler1 = float(self.datafile['SEMFields']['DOEuler1'])
            doeuler2 = float(self.datafile['SEMFields']['DOEuler2'])
            doeuler3 = float(self.datafile['SEMFields']['DOEuler3'])
            sem_fields.detector_orientation_euler = np.array(
                [doeuler1, doeuler2, doeuler3]
            )
        if self.extension == 'h5oina':
            sem_fields.detector_orientation_euler = self.rad2deg(
                self.datafile['Detector Orientation Euler'][()][0]
            )

    def parse_stage_position(self):
        stage_position = self.output_data.m_create(ebsd.StagePosition)
        if self.extension == 'cpr':
            stage_position.x_axis = float(self.datafile['StagePosition']['XPos'])
            stage_position.y_axis = float(self.datafile['StagePosition']['YPos'])
            stage_position.z_axis = float(self.datafile['StagePosition']['ZPos'])
            stage_position.rotation = float(self.datafile['StagePosition']['RPos'])
            stage_position.tilt = float(self.datafile['StagePosition']['TPos'])
        if self.extension == 'h5oina':
            stage_position.x_axis = self.datafile['Stage Position']['X'][()]
            stage_position.y_axis = self.datafile['Stage Position']['Y'][()]
            stage_position.z_axis = self.datafile['Stage Position']['Z'][()]
            stage_position.rotation = self.rad2deg(
                self.datafile['Stage Position']['Rotation'][()]
            )
            stage_position.tilt = self.rad2deg(
                self.datafile['Stage Position']['Tilt'][()]
            )

    def parse_acquisition_surface(self):
        acquisition_surface = self.output_data.m_create(ebsd.AcquisitionSurface)
        if self.extension == 'cpr':
            euler1 = float(self.datafile['Acquisition Surface']['Euler1'])
            euler2 = float(self.datafile['Acquisition Surface']['Euler2'])
            euler3 = float(self.datafile['Acquisition Surface']['Euler3'])
            acquisition_surface.surface_orientation_euler = np.array(
                [euler1, euler2, euler3]
            )
        if self.extension == 'h5oina':
            acquisition_surface.surface_orientation_euler = self.rad2deg(
                self.datafile['Specimen Orientation Euler'][()][0]
            )

    def parse_phase(self, phase_name):
        phase = self.output_data.m_create(ebsd.Phase)
        if self.extension == 'cpr':
            phase.name = phase_name
            phase.structure_name = self.datafile[phase_name]['StructureName']
            phase.reference = self.datafile[phase_name]['Reference']
            a_lattice = float(self.datafile[phase_name]['a'])
            b_lattice = float(self.datafile[phase_name]['b'])
            c_lattice = float(self.datafile[phase_name]['c'])
            alpha_lattice = float(self.datafile[phase_name]['alpha'])
            beta_lattice = float(self.datafile[phase_name]['beta'])
            gamma_lattice = float(self.datafile[phase_name]['gamma'])
            phase.lattice_dimensions = np.array([a_lattice, b_lattice, c_lattice])
            phase.lattice_angles = np.array(
                [alpha_lattice, beta_lattice, gamma_lattice]
            )
            phase.laue_group = int(self.datafile[phase_name]['LaueGroup'])
            phase.space_group = int(self.datafile[phase_name]['SpaceGroup'])
            phase.nb_reflectors = int(self.datafile[phase_name]['NumberOfReflectors'])
        if self.extension == 'h5oina':
            phase.name = phase_name
            phase.structure_name = self.datafile['Phases'][phase_name][
                'Phase Name'
            ].asstr()[0]
            phase.reference = self.datafile['Phases'][phase_name]['Reference'].asstr()[
                0
            ]
            phase.lattice_dimensions = self.datafile['Phases'][phase_name][
                'Lattice Dimensions'
            ][()][0]
            phase.lattice_angles = self.rad2deg(
                self.datafile['Phases'][phase_name]['Lattice Angles'][()][0]
            )
            phase.laue_group = self.datafile['Phases'][phase_name]['Laue Group'][()]
            phase.space_group = self.datafile['Phases'][phase_name]['Space Group'][()]
            phase.nb_reflectors = self.datafile['Phases'][phase_name][
                'Number Reflectors'
            ][()]

    def parse_phases(self):
        if self.extension == 'cpr':
            phases = [
                section
                for section in self.datafile.sections()
                if section.startswith('Phase') and section != 'Phases'
            ]
            for phase in phases:
                self.parse_phase(phase)
        if self.extension == 'h5oina':
            for phase in self.datafile['Phases']:
                self.parse_phase(phase)

    def parse(
        self,
        mainfile: str,
        archive: 'EntryArchive',
        logger: 'BoundLogger',
        child_archives: dict[str, 'EntryArchive'] = None,
    ) -> None:
        self.mainfile = mainfile
        self.archive = archive
        self.maindir = os.path.dirname(self.mainfile)
        self.mainfile = os.path.basename(self.mainfile)
        self.logger = logging.getLogger(__name__) if logger is None else logger

        self.output_data = ebsd.EBSDOutput()
        archive.data = self.output_data

        self.extension = mainfile.split('.')[-1]

        if self.extension == 'cpr':
            import configparser

            self.datafile = configparser.ConfigParser()
            self.datafile.read(mainfile)

        if self.extension == 'h5oina':
            import h5py

            try:
                self.datah5 = h5py.File(self.mainfile)
                self.datafile = self.datah5['1']['EBSD']['Header']
            except Exception:
                self.logger.error('Error opening h5 file.')
                return

        self.parse_output()
        self.parse_job()
        self.parse_semfields()
        self.parse_stage_position()
        self.parse_acquisition_surface()
        self.parse_phases()
