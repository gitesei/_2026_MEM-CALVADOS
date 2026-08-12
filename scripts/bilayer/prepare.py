import os
from calvados.cfg import Config, Job, Components
import subprocess
import numpy as np
import pandas as pd
from argparse import ArgumentParser
from Bio import SeqIO

parser = ArgumentParser()
parser.add_argument('--name',nargs='?',required=True,type=str)
parser.add_argument('--frac',nargs='?',required=True,type=int)
parser.add_argument('--secondary',nargs='?',default='DPPC',type=str)
#parser.add_argument('--gpu_id',nargs='?',required=True,type=int)
args = parser.parse_args()

# Dictionary to define starting APL (from M3)
eq_apl_dict = {
    'DOPC': 0.67,
    'POPC': 0.63,
    'DOPS': 0.66,
    'POPS': 0.64
}

cwd = os.getcwd()
N_save = int(1e5)
N_frames = 750
Lx = 25
Ly = Lx
area_per_lipid = eq_apl_dict[args.name]
N_lipids = int(np.ceil(Lx*Ly/area_per_lipid)*2)

if args.frac < 100:
    sysname = f'{args.name}_{args.frac}_{args.secondary}_{100-args.frac}'
else:
    sysname = f'{args.name}_{args.frac}'

residues_file = f'{cwd}/input/residues.csv'

config = Config(
  # GENERAL
  sysname = sysname, # name of simulation system
  box = [Lx, Ly, 60.], # nm
  temp = 297.15,
  ionic = 0.15, # molar
  pH = 7,
  topol = 'bilayer',
  bilayer_eq = True,
  friction = 0.01,
  pressure_coupling = True,
  pressure = [0,0,0],

  # RUNTIME SETTINGS
  #gpu_id = args.gpu_id,
  wfreq = N_save, # dcd writing frequency, 1 = 10fs
  steps = N_frames*N_save, # number of simulation steps
  steps_eq = 50*N_save,
  runtime = 0, # overwrites 'steps' keyword if > 0
  platform = 'CUDA', # 'CUDA' or 'OpenCL'
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
from calvados.analysis import SlabAnalysis, calc_bilayer_prop

slab = SlabAnalysis(name="{sysname:s}", input_path="{path:s}",
                    output_path="{output_path:s}", ref_name="{sysname:s}", verbose=True)

slab.center(start=350, center_target='all')
slab.calc_profiles()
calc_bilayer_prop(path="{path:s}",sysname="{sysname:s}",output_path="{output_path:s}")
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
  fresidues = fresidues_to_use, # residue definitions
)
components.add(name=args.name, molecule_type='lipid', nmol=int(N_lipids*args.frac/100))
if args.frac < 100:
    components.add(name=args.secondary, molecule_type='lipid', nmol=int((100-args.frac)*N_lipids/100))
components.write(path,name='components.yaml')
