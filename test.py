import random

name = ["AL", "John", "Tanaka", "AL"]

amount = [200, 1200, 5000, 200, 1000]

dictionary = {}

# remove duplicate names
name = list(set(name))

# make keys and initialize if there's not exist
for i in range(len(name)):
    dictionary[name[i]] = 0

for i in range(5):
    n = random.choice(name)
    a = random.choice(amount)
    dictionary[n] = a + dictionary[n]
    print(f"name: {n}")
    print(f"amount: {a}")
    print("##################")

print(dictionary)