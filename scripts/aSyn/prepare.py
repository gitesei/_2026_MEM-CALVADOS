import os
from calvados.cfg import Config, Job, Components
import subprocess
import numpy as np
import pandas as pd
from argparse import ArgumentParser
from Bio import SeqIO

parser = ArgumentParser()
parser.add_argument('--name',nargs='?',required=True,type=str)
parser.add_argument('--replica',nargs='?',required=True,type=int)
args = parser.parse_args()

cwd = os.getcwd()
N_save = int(5e4)
N_frames = 10000
Lx = 20
Ly = Lx
area_per_lipid = .65
N_lipids = int(np.ceil(Lx*Ly/area_per_lipid)*2)

sysname = f'{args.name:s}_{args.replica:d}'
residues_file = f'{cwd}/input/residues.csv'

pH = 7.0

config = Config(
  # GENERAL
  sysname = sysname, # name of simulation system
  box = [Lx, Ly, 100.], # nm
  temp = 298.15,
  ionic = 0.05, # molar
  pH = pH,
  topol = 'shift_ref_bead',
  bilayer_eq = True,
  friction = 0.01,
  pressure_coupling = True,
  pressure = [0,0,0],
  report_potential_energy = False,

  # RUNTIME SETTINGS
  gpu_precision = 'single',
  wfreq = N_save, # dcd writing frequency, 1 = 10fs
  logfreq = N_save,
  steps = N_frames*N_save, # number of simulation steps
  steps_eq = 20*N_save,
  runtime = 0, # overwrites 'steps' keyword if > 0
  platform = 'CUDA', # 'CUDA'
  restart = 'checkpoint',
  frestart = 'restart.chk'
)

# PATH
path = f'{cwd}/{sysname}'
output_path = 'data'
subprocess.run(f'mkdir -p {path}',shell=True)
subprocess.run(f'mkdir -p {output_path}',shell=True)

config.write(path,name='config.yaml')

components = Components(
  # Defaults
  molecule_type = 'protein',
  nmol = 16, # number of molecules
  restraint = False, # apply restraints
  charge_termini = 'None', # charge N or C or both

  # INPUT
  ffasta = f'{cwd}/input/fastalib.fasta', # input fasta file
  fresidues = residues_file, # residue definitions
  fdomains = f'{cwd}/input/domains.yaml', # domain definitions (harmonic restraints)
  pdb_folder = f'{cwd}/input', # directory for pdb and PAE files
)
components.add(name='POPC', molecule_type='lipid', nmol=int(N_lipids*0.4))
components.add(name='POPS', molecule_type='lipid', nmol=int(N_lipids*0.6))
if args.name == 'aSyn':
    components.add(name=args.name, restraint=False, charge_termini='both', ref_bead=-1, pos_bead=[0,0,40], nmol=16)
elif args.name in ['aSyn_LH']:
    components.add(name=args.name, restraint=True, charge_termini='both', ref_bead=-1, pos_bead=[0,0,40], nmol=16,
            restraint_type="harmonic")
else:
    components.add(name=args.name, restraint=True, charge_termini='both', ref_bead=-1, pos_bead=[0,0,40],
        restraint_type='go', k_go=15., colabfold=0, nmol=16)
components.write(path,name='components.yaml')

