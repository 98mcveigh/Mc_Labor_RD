import pickle

test = ["hello","goodbye","siyanara"]

file = open("settings.dat","rb")
dict = pickle.load(file)
print(dict)
file.close()
