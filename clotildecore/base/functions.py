def slugify(text):
    T=text.lower().replace(" ","_")
    T=T.replace("-","")
    T=T.replace("/","_")
    return T

