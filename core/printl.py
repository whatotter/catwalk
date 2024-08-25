def info(string, *args, **kwargs):
    print("\033[0;34m\033[1m[INFO]\033[0m {}".format(string), *args, **kwargs)

def warn(string, *args, **kwargs):
    print("\033[1;33m\033[1m[WARN]\033[0m {}".format(string), *args, **kwargs)