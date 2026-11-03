import os
from calvados.cfg import Config, Job, Components
import subprocess
import numpy as np
from argparse import ArgumentParser
from Bio import SeqIO

parser = ArgumentParser()
parser.add_argument('--name',nargs='?',required=True,type=str)
parser.add_argument('--replica',nargs='?',required=True,type=int)
args = parser.parse_args()

ref_bead = 131
tmd_sel = "resid 46 to 243"

cwd = os.getcwd()
N_save = int(5e4)
N_frames = 500
Lx = 25
Ly = Lx
area_per_lipid = .63
N_lipids = int(np.ceil(Lx*Ly/area_per_lipid)*2)

sysname = f'{args.name:s}_{args.replica:d}'
residues_file = f'{cwd}/input/residues.csv'

config = Config(
  # GENERAL
  sysname = sysname, # name of simulation system
  box = [Lx, Ly, 100.], # nm
  temp = 293.15,
  ionic = 0.15, # molar
  pH = 7.4,
  topol = 'shift_ref_bead',
  bilayer_eq = True,
  friction = 0.01,
  pressure_coupling = True,
  pressure = [0,0,0],

  # RUNTIME SETTINGS
  #gpu_id = args.gpu_id,
  wfreq = N_save, # dcd writing frequency, 1 = 10fs
  logfreq = 100*N_save,
  steps = N_frames*N_save, # number of simulation steps
  steps_eq = 0*N_save,
  runtime = 0, # overwrites 'steps' keyword if > 0
  platform = 'CUDA', # 'CUDA'
  restart = 'checkpoint',
  frestart = 'restart.chk',
  verbose = True,
)

# PATH
path = f'{cwd}/{sysname}'
output_path = 'data'
subprocess.run(f'mkdir -p {path}',shell=True)
subprocess.run(f'mkdir -p {output_path}',shell=True)

analyses = f"""
from calvados.analysis import calc_membrane_profiles, calc_com_profiles, calc_domain_angles, calc_domain_rgs

chainid_dict = dict({args.name}=(0,0))
calc_membrane_profiles("{path}","{sysname}","{output_path}","{residues_file}","{tmd_sel}",100)
calc_com_profiles("{path:s}","{sysname:s}","{output_path:s}","{residues_file:s}",chainid_dict=chainid_dict)
angle_sels = dict(TMD="{tmd_sel}")
calc_domain_angles("{path}","{sysname}","{output_path}",angle_sels,0.5)
"""

config.write(path,name='config.yaml',analyses=analyses)

components = Components(
  # Defaults
  molecule_type = 'protein',
  nmol = 1, # number of molecules
  restraint = False, # apply restraints
  charge_termini = 'None', # charge N or C or both

  # INPUT
  ffasta = f'{cwd}/input/fastalib.fasta', # input fasta file
  fresidues = f'{cwd}/input/residues.csv', # residue definitions
  pdb_folder = f'{cwd}/input', # directory for pdb and PAE files

  # RESTRAINTS
  restraint_type = 'go', # harmonic (CALVADOS 3) or go (AF-CALVADOS)
  use_com = True, # apply on centers of mass instead of CA
  colabfold = 0, # PAE format (EBI AF=0, Colabfold=1&2)
  k_go = 15., # Restraint force constant
)

components.add(name='POPC', molecule_type='lipid', nmol=N_lipids)
components.add(name=args.name, restraint=True, charge_termini='both', ref_bead=ref_bead)
components.write(path,name='components.yaml')

