machines = [(2, 4), (3, 8)]
print machines
a = sorted(machines, reverse=True, key=lambda x: x[1])
print machines
print a