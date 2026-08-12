import os
import time
import shutil
import subprocess
from jinja2 import Template

submission = Template("""#!/bin/bash
#SBATCH --job-name={{name}}_{{replica}}
#SBATCH --gres=gpu:1
#SBATCH -t 72:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH -A naiss2026-3-355-gpu
#SBATCH -p gpu
#SBATCH -o {{name}}_{{replica}}.out
#SBATCH -e {{name}}_{{replica}}.err

module load GPU/Miniforge/26.3.2-2-eb
conda activate calvados

python prepare.py --name {{name}}
python {{name}}/run.py --path {{name}}""")

peptides = ['WLFLL', 'WLLLL', 'WLMLL', 'WLILL', 'WLVLL', 'WLWLL', 'WLYLL']

for name in peptides:
    if not os.path.isdir(name):
        os.mkdir(name)
    with open(f'{name}.sh', 'w') as submit:
        submit.write(submission.render(name=name))
    subprocess.run(['sbatch',f'{name}.sh'])
    time.sleep(0.5)
