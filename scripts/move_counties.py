import os

for fn in os.listdir("states"):
    fn = os.path.join("states", fn)
    if os.path.isdir(fn):
        os.makedirs(os.path.join(fn, "counties"), exist_ok=True)
        for d in os.listdir(fn):
            new = os.path.join(fn, "counties", d)
            old = os.path.join(fn, d)
            if not os.path.isdir(old) or d == "counties":
                continue
            os.rename(old, new)
