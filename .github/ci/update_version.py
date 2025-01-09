import sys, pathlib, os, json

path = pathlib.Path("..", "..", "plugin.json")
hash = sys.argv[-1]
with path.open("r") as f:
    data = json.load(f)


ver: str = data['Version']
if ver.endswith(("a", "b")):
    data['Version'] = ver + hash
    print(data)
    with path.open("w") as f:
        json.dump(data, f, indent=4) 