import os
from calvados.cfg import Config, Job, Components
import subprocess
import numpy as np
import pandas as pd
from argparse import ArgumentParser
from Bio import SeqIO

parser = ArgumentParser()
parser.add_argument('--name_1',nargs='?',required=True,type=str)
parser.add_argument('--name_2',nargs='?',required=True,type=str)
parser.add_argument('--replica',nargs='?',required=True,type=int)
args = parser.parse_args()

ref_bead = 15
tmd_sel = "resid 4 to 26"

cwd = os.getcwd()
N_save = int(5e4)
N_frames = 2400
Lx = 30
Ly = Lx
area_per_lipid = .67
N_lipids = int(np.ceil(Lx*Ly/area_per_lipid)*2)

sysname = f'{args.name_1:s}_{args.name_2:s}_Sos1_{args.replica:d}'
residues_file = f'{cwd}/input/residues.csv'

pH = 7.4

# set charge on pTyr based on input pH
#pKa_dict = dict(TYP=5.83)
#df_residues = pd.read_csv(residues_file,index_col='three')
#for pres in pKa_dict.keys():
#    df_residues.loc[pres,'q'] = - 1 - 1 / (1 + 10**(pKa_dict[pres]-pH))
#df_residues.reset_index().set_index('one').to_csv(residues_file)

config = Config(
  # GENERAL
  sysname = sysname, # name of simulation system
  box = [Lx, Ly, 150.], # nm
  temp = 293.15,
  ionic = 0.15, # molar
  pH = pH,
  topol = 'shift_ref_bead',
  bilayer_eq = True,
  friction = 0.01,
  pressure_coupling = True,
  pressure = [0,0,0],
  report_potential_energy = True,

  # RUNTIME SETTINGS
  gpu_precision = 'single',
  wfreq = N_save, # dcd writing frequency, 1 = 10fs
  logfreq = N_save,
  steps = N_frames*N_save, # number of simulation steps
  steps_eq = 10*N_save,
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
ref_sel="resname TDO or resname TPO"
strip_sel="not (resname SEB or resname CHO or resname PHO or resname MID or resname TDO or resname TPO)"

analyses = f"""
from calvados.analysis import calc_membrane_profiles, calc_com_traj, calc_com_profiles, cmap_chain_pairs

calc_membrane_profiles("{path}","{sysname}","{output_path}","{residues_file}","{tmd_sel}",600,"{ref_sel}","{strip_sel}")
chainid_dict = dict({args.name_1}=(0, 15), {args.name_2}=(16, 47), Sos1=(48,79))
calc_com_traj(path="{path:s}",sysname="{sysname:s}",output_path="{output_path:s}",residues_file="{residues_file:s}",
                  chainid_dict=chainid_dict)
calc_com_profiles(path="{path:s}",sysname="{sysname:s}",output_path="{output_path:s}",residues_file="{residues_file:s}",
                  chainid_dict=chainid_dict)
cmap_chain_pairs(path="{path:s}",sysname="{sysname:s}",output_path="{output_path:s}",chainid_dict=chainid_dict)
"""

config.write(path,name='config.yaml')#,analyses=analyses)

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
components.add(name='DOPC', molecule_type='lipid', nmol=N_lipids)
components.add(name=args.name_1, restraint=True, charge_termini='both', ref_bead=ref_bead, nmol=16)
components.add(name=args.name_2, restraint=True, charge_termini='both', ref_bead=-1, pos_bead=[0,0,10],
        restraint_type='go', k_go=15., colabfold=0, nmol=32)
components.add(name='Sos1', restraint=False, charge_termini='both', ref_bead=-1, pos_bead=[0,0,10], nmol=32)
components.write(path,name='components.yaml')

