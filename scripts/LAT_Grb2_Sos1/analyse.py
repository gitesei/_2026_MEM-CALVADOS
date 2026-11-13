import os
from calvados.cfg import Config, Job, Components
import subprocess
import numpy as np
import pandas as pd
from argparse import ArgumentParser
from Bio import SeqIO
import mdtraj as md
from calvados.analysis import calc_bilayer_prop, calc_com_profiles, cmap_chain_pairs

parser = ArgumentParser()
parser.add_argument('--name_1',nargs='?',required=True,type=str)
parser.add_argument('--name_2',nargs='?',required=True,type=str)
parser.add_argument('--replica',nargs='?',required=True,type=int)
args = parser.parse_args()

cwd = os.getcwd()

ref_bead = 15
tmd_sel = "resid 4 to 26"

sysname = f'{args.name_1:s}_{args.name_2:s}_Sos1_{args.replica:d}'
residues_file = f'{cwd}/input/residues.csv'

# PATH
path = f'{cwd}/{sysname}'
output_path = 'data'
subprocess.run(f'mkdir -p {path}',shell=True)
subprocess.run(f'mkdir -p {output_path}',shell=True)

ref_sel="resname TDO or resname TPO"
strip_sel="not (resname SEB or resname CHO or resname PHO or resname MID or resname TDO or resname TPO)"

calc_bilayer_prop(path,sysname,output_path,residues_file,start=390)
chainid_dict = {args.name_1: (0, 15), args.name_2: (16, 47), "Sos1": (48, 79)}
calc_com_profiles(path,sysname,output_path,residues_file,chainid_dict=chainid_dict)
cmap_chain_pairs(path,sysname,output_path,chainid_dict=chainid_dict)
