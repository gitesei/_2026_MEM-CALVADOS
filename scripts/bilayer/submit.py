import os
import time
import shutil
import subprocess
from jinja2 import Template

submission = Template("""#!/bin/sh
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -p gpua100i
#SBATCH --gres=gpu:1
#SBATCH -A lu2025-2-64
#SBATCH -t 24:0:0
#SBATCH -J {{sysname}}
#SBATCH -o {{sysname}}/out
#SBATCH -e {{sysname}}/err

source /home/riccardosaltutti/.bashrc
conda activate calvados
module load CUDA/12.0.0

python prepare.py --name {{name}} --frac {{frac}} --secondary {{secondary}}
python {{sysname}}/run.py --path {{sysname}}""")

lipids = ['POPS']

fractions = [50]

secondary_lipid = 'POPC' #not used if frac = 100

for name in lipids:
    for frac in fractions:
        if frac < 100:
            sysname = f'{name}_{frac}_{secondary_lipid}_{100-frac}'
        else:
            sysname = f'{name}_{frac}'
        if not os.path.isdir(sysname):
            os.mkdir(sysname)
            with open(f'{sysname}.sh', 'w') as submit:
                submit.write(submission.render(name=name, frac=frac, secondary=secondary_lipid, sysname=sysname))
            subprocess.run(['sbatch',f'{sysname}.sh'])
            time.sleep(0.5)
