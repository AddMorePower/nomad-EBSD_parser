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
            general_cpr = self.datafile['General']
            self.output_data.format_version = general_cpr['Version']
            self.output_data.date = general_cpr['Date']
            self.output_data.description = general_cpr['Description']
            self.output_data.notes = general_cpr['Notes']
            self.output_data.project_notes = general_cpr['ProjectNotes']
        if self.extension == 'h5oina':
            self.output_data.format_version = self.datah5['Format Version'].asstr()[0]
            self.output_data.date = self.datafile['Acquisition Date'].asstr()[0]
            self.output_data.description = (
                self.datafile['Project Label'].asstr()[0]
                + self.datafile['Specimen Label'].asstr()[0]
            )
            self.output_data.notes = self.datafile['Specimen Notes'].asstr()[0]
            self.output_data.project_notes = self.datafile['Project Notes'].asstr()[0]
            self.output_data.site_label = self.datafile['Site Label'].asstr()[0]

    def parse_job(self):
        job = self.output_data.m_create(ebsd.Job)
        if self.extension == 'cpr':
            job_cpr = self.datafile['Job']
            job.magnification = float(job_cpr['Magnification'])
            job.beam_voltage = float(job_cpr['kV'])
            job.nb_points = int(job_cpr['NoOfPoints'])
            job.tilt_angle = float(job_cpr['TiltAngle'])
            job.tilt_axis = float(job_cpr['TiltAxis'])
            job.x_cells = int(job_cpr['xCells'])
            job.y_cells = int(job_cpr['yCells'])
        if self.extension == 'h5oina':
            job.magnification = self.datafile['Magnification'][()]
            job.beam_voltage = self.datafile['Beam Voltage'][()]
            job.nb_points = self.datafile['X Cells'][()] * self.datafile['Y Cells'][()]
            job.tilt_angle = self.rad2deg(self.datafile['Tilt Angle'][()])
            job.tilt_axis = self.rad2deg(self.datafile['Tilt Axis'][()])
            job.x_cells = self.datafile['X Cells'][()]
            job.y_cells = self.datafile['Y Cells'][()]
            job.working_distance = self.datafile['Working Distance'][()]
            job.insertion_distance = self.datafile['Detector Insertion Distance'][()]
            job.auto_background_correction = self.datafile['Auto Background Correction'][()]
            job.static_background_correction = self.datafile['Static Background Correction'][()]
            job.x_step = self.datafile['X Step'][()]
            job.bounding_box_size = self.datafile['Bounding Box Size'][()]
            job.hit_rate = self.datafile['Hit Rate'][()]

    def parse_camera(self):
        if self.extension == 'h5oina':
            camera = self.output_data.m_create(ebsd.Camera)
            camera.camera_binning_mode = self.datafile['Camera Binning Mode'].asstr()[0]
            camera.camera_exposure_time = self.datafile['Camera Exposure Time'][()]
            camera.camera_gain = self.datafile['Camera Gain'][()]

    def parse_semfields(self):
        sem_fields = self.output_data.m_create(ebsd.SEMFields)
        if self.extension == 'cpr':
            doeuler_cpr = self.datafile['SEMFields']
            doeuler1 = float(doeuler_cpr['DOEuler1'])
            doeuler2 = float(doeuler_cpr['DOEuler2'])
            doeuler3 = float(doeuler_cpr['DOEuler3'])
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
            stage_pos_cpr = self.datafile['StagePosition']
            stage_position.x_axis = float(stage_pos_cpr['XPos'])
            stage_position.y_axis = float(stage_pos_cpr['YPos'])
            stage_position.z_axis = float(stage_pos_cpr['ZPos'])
            stage_position.rotation = float(stage_pos_cpr['RPos'])
            stage_position.tilt = float(stage_pos_cpr['TPos'])
        if self.extension == 'h5oina':
            stage_pos_h5 = self.datafile['Stage Position']
            stage_position.x_axis = stage_pos_h5['X'][()]
            stage_position.y_axis = stage_pos_h5['Y'][()]
            stage_position.z_axis = stage_pos_h5['Z'][()]
            stage_position.rotation = self.rad2deg(stage_pos_h5['Rotation'][()])
            stage_position.tilt = self.rad2deg(stage_pos_h5['Tilt'][()])

    def parse_acquisition_surface(self):
        acquisition_surface = self.output_data.m_create(ebsd.AcquisitionSurface)
        if self.extension == 'cpr':
            euler_cpr = self.datafile['Acquisition Surface']
            euler1 = float(euler_cpr['Euler1'])
            euler2 = float(euler_cpr['Euler2'])
            euler3 = float(euler_cpr['Euler3'])
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
            phase_cpr = self.datafile[phase_name]
            phase.name = phase_name
            phase.structure_name = phase_cpr['StructureName']
            phase.reference = phase_cpr['Reference']
            a_lattice = float(phase_cpr['a'])
            b_lattice = float(phase_cpr['b'])
            c_lattice = float(phase_cpr['c'])
            alpha_lattice = float(phase_cpr['alpha'])
            beta_lattice = float(phase_cpr['beta'])
            gamma_lattice = float(phase_cpr['gamma'])
            phase.lattice_dimensions = np.array([a_lattice, b_lattice, c_lattice])
            phase.lattice_angles = np.array(
                [alpha_lattice, beta_lattice, gamma_lattice]
            )
            phase.laue_group = int(phase_cpr['LaueGroup'])
            phase.space_group = int(phase_cpr['SpaceGroup'])
            phase.nb_reflectors = int(phase_cpr['NumberOfReflectors'])
        if self.extension == 'h5oina':
            phase.name = phase_name
            phase_h5 = self.datafile['Phases'][phase_name]
            phase.structure_name = phase_h5['Phase Name'].asstr()[0]
            phase.reference = phase_h5['Reference'].asstr()[0]
            phase.lattice_dimensions = phase_h5['Lattice Dimensions'][()][0]
            phase.lattice_angles = self.rad2deg(phase_h5['Lattice Angles'][()][0])
            phase.laue_group = phase_h5['Laue Group'][()]
            phase.space_group = phase_h5['Space Group'][()]
            phase.nb_reflectors = phase_h5['Number Reflectors'][()]

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
        self.filename = os.path.basename(self.mainfile)
        self.logger = logging.getLogger(__name__) if logger is None else logger

        self.output_data = ebsd.EBSDOutput()
        archive.data = self.output_data

        self.extension = self.filename.split('.')[-1]

        if self.extension == 'cpr':
            import configparser

            self.datafile = configparser.ConfigParser()
            self.datafile.read(mainfile)

        if self.extension == 'h5oina':
            import h5py

            try:
                self.datah5 = h5py.File(self.mainfile)
            except Exception as err:
                self.logger.error(f'Error opening h5 file.\n{err}')
                return

            self.datafile = self.datah5['1']['EBSD']['Header']

        self.parse_output()
        self.parse_job()
        self.parse_camera()
        self.parse_semfields()
        self.parse_stage_position()
        self.parse_acquisition_surface()
        self.parse_phases()
