from pathlib import Path

for file in Path('./items').iterdir():
    if file.is_file():
        print(file.name)
