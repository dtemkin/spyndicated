import os


def find_next_filename(directory, filename):
    f, ext = os.path.splitext(filename)
    files = [os.path.splitext(f)[0] for f in os.listdir(directory)]
    existing = list(filter(lambda x: x.find(f) > -1, files))
    if len(existing) > 0:
        if os.path.isfile(os.path.join(directory, f + str(len(existing)) + ext)):
            raise ValueError("Unable to determine next valid filename")
        else:
            return os.path.join(directory, f + str(len(existing)) + ext)
    else:
        return os.path.join(directory, f + ext)
