outFile = str(input("Enter the name of the input file(default: grp30.in): "))
outFile = outFile.strip()
if len(outFile) == 0:
    outFile = "grp30.in"
else:
    size = len(outFile) - 1
    if outFile[size - 3:] != ".in":
        outFile = outFile + ".in"

import random
with open(outFile, "w+") as i:
    l = int(random.randint(1, 8))
    n = int(random.randint(1, 30))
    i.write(f"{l}\n{n}\n")
    '''
    print(l)
    print(n)
    '''
    #jobs cannot exceed 100
    upper_bound = 100
    for _ in range(n):
        m = int(random.randint(1, upper_bound))
        upper_bound = upper_bound - m
        w = float(random.uniform(0.000001, 64.0))
        i.write(f"{m}\n{w:.6f}\n")
        '''
        print(m)
        print(w)
        '''
        jc = 0 #job count
        for __ in range(m):
            s = int(random.randint(1, l))
            d = int(random.randint(1, 96))
            if jc > 0:
                p = int(random.randint(0, jc))
            else:
                p = 0
            if p > jc:
                p = p % jc
            print(p, m)
            jc += 1
            i.write(f"{s} {d} {p}")
            '''
            print(s, end=" ")
            print(d, end=" ")
            print(p, end=" ")
            '''
            dep = set()
            for ___ in range(p):
                a = random.randint(1, jc)
                if a > jc:
                    a = a % jc
                if a not in dep:
                    i.write(f" {a}")
                    #print(a, end=" ")
                    dep.add(a)
                    continue
                while True:
                    a = random.randint(1, jc)
                    if a not in dep:
                        i.write(f" {a}")
                        #print(a, end=" ")
                        dep.add(a)
                        break

            i.write("\n")
            del dep
