import os
import time
import shutil
import subprocess
from jinja2 import Template

submission = Template("""#!/bin/bash
#SBATCH --job-name={{name}}_{{replica}}
#SBATCH --gres=gpu:1
#SBATCH -t 24:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH -A naiss2026-3-355-gpu
#SBATCH -p gpu
#SBATCH -o {{name}}_{{replica}}.out
#SBATCH -e {{name}}_{{replica}}.err

module load GPU/Miniforge/26.3.2-2-eb
mamba activate calvados

python prepare.py --name {{name}} --replica {{replica}}

python {{name}}_{{replica}}/run.py --path {{name}}_{{replica}}
""")

for name in ['GHR']:
    for replica in range(5):
        if not os.path.isdir(f'{name:s}_{replica:d}'):
            os.mkdir(f'{name:s}_{replica:d}')
        with open(f'{name:s}_{replica:d}.sh', 'w') as submit:
            submit.write(submission.render(name=name,replica=replica))
        subprocess.run(['sbatch',f'{name:s}_{replica:d}.sh'])
        time.sleep(0.5)
