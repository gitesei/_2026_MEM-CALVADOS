import os
import time
import shutil
import subprocess
import mdtraj as md
from jinja2 import Template

submission = Template("""#!/bin/sh
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu
#SBATCH -t 28:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=10G
#SBATCH -A naiss2026-3-355-gpu
#SBATCH -J {{name}}_{{replica}}
#SBATCH -o {{name}}_{{replica}}/out
#SBATCH -e {{name}}_{{replica}}/err

module load GPU/Miniforge/26.3.2-2-eb

mamba activate memcal

python prepare.py --name {{name}} --replica {{replica}}

python {{name}}_{{replica}}/run.py --path {{name}}_{{replica}} &

wait
""")

for name in ['aSyn','aSyn_LH']:
    for replica in [3]:
        if not os.path.isdir(f'{name}_{replica}'):
            os.mkdir(f'{name}_{replica}')
        with open(f'{name}_{replica}.sh', 'w') as submit:
            submit.write(submission.render(name=name,replica=replica))
        subprocess.run(['sbatch',f'{name}_{replica}.sh'])
        time.sleep(0.5)
