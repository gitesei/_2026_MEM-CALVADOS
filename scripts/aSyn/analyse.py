import os
from calvados.cfg import Config, Job, Components
import subprocess
import numpy as np
import pandas as pd
from argparse import ArgumentParser
from Bio import SeqIO
import mdtraj as md
from calvados.analysis import calc_bilayer_prop, cmap_selection

parser = ArgumentParser()
parser.add_argument('--name',nargs='?',required=True,type=str)
parser.add_argument('--replica',nargs='?',required=True,type=int)
args = parser.parse_args()

cwd = os.getcwd()

ref_sel="resname TDO or resname TPO"

sysname = f'{args.name:s}_{args.replica:d}'
residues_file = f'{cwd}/input/residues.csv'

# PATH
path = f'{cwd}/{sysname}'
output_path = 'data'
subprocess.run(f'mkdir -p {path}',shell=True)
subprocess.run(f'mkdir -p {output_path}',shell=True)

calc_bilayer_prop(path,sysname,output_path,residues_file,100,10000)
indexrange_sels = {
    "1_lipids": ("resindex 0 to 139", "not resindex 0 to 2239"),
    "2_lipids": ("resindex 140 to 279", "not resindex 0 to 2239"),
    "3_lipids": ("resindex 280 to 419", "not resindex 0 to 2239"),
    "4_lipids": ("resindex 420 to 559", "not resindex 0 to 2239"),
    "5_lipids": ("resindex 560 to 699", "not resindex 0 to 2239"),
    "6_lipids": ("resindex 700 to 839", "not resindex 0 to 2239"),
    "7_lipids": ("resindex 840 to 979", "not resindex 0 to 2239"),
    "8_lipids": ("resindex 980 to 1119", "not resindex 0 to 2239"),
    "9_lipids": ("resindex 1120 to 1259", "not resindex 0 to 2239"),
    "10_lipids": ("resindex 1260 to 1399", "not resindex 0 to 2239"),
    "11_lipids": ("resindex 1400 to 1539", "not resindex 0 to 2239"),
    "12_lipids": ("resindex 1540 to 1679", "not resindex 0 to 2239"),
    "13_lipids": ("resindex 1680 to 1819", "not resindex 0 to 2239"),
    "14_lipids": ("resindex 1820 to 1959", "not resindex 0 to 2239"),
    "15_lipids": ("resindex 1960 to 2099", "not resindex 0 to 2239"),
    "16_lipids": ("resindex 2100 to 2239", "not resindex 0 to 2239"),
}
cmap_selection(path,sysname,output_path,indexrange_sels)
