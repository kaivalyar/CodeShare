dic = {}
with open("authors.k", "w") as g:
    g.write(str(dic)) # Map from code to number ie {"kaiv":2015}
with open("codes.k", "w") as g:
    g.write(str(dic)) # Map from name to code ie {"Kaivalya Rawal":"kaiv"}
