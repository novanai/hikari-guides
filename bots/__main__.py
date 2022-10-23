import os
import runpy
import sys

import dotenv

dotenv.load_dotenv()

if len(sys.argv) > 1:
    runpy.run_path(os.path.join("bots", f"{sys.argv[1]}.py"))
else:
    print("Please provide a file to run")
