from pathlib import Path
exec(compile((Path(__file__).parent/'package_v32.py').read_text(),str(Path(__file__).parent/'package_v32.py'),'exec'))
