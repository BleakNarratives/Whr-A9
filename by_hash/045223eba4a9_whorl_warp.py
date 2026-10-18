import sys, importlib, json
def warp(lib_name, func_name, *args):
    lib = importlib.import_module(lib_name)
    func = getattr(lib, func_name)
    print(json.dumps(func(*args)))

if __name__ == "__main__":
    warp(sys.argv[1], sys.argv[2], *sys.argv[3:])
