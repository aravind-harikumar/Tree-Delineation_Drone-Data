# Lists
samplelist = ['1', '2', '3']
samplelist.index('3')
samplelist.insert(0,'122')
# samplelist.remove(122)
# samplelist.pop()
samplelist.sort(key=str.lower,reverse = True)
print(samplelist)
# Sets
s = {}

# L = [("Alice", 25), ("Bob", 20), ("Alex", 5)]
# L.sort(key=lambda x: x[1])
# print(L)

# class User:
#     def __init__(self, name, age):
#         self.name = name
#         self.age = age

# Bob = User('Bob', 20)
# Alice = User('Alice', 30)
# Leo = User('Leo', 15)
# L = [Bob, Alice, Leo]

# L.sort(key=lambda x: x.name)
# print([item.name for item in L])

# print([i for i in range(1,100,1) if(i%2==0)])
s1 = (1,0)
s1 += (2,)
print(s1)

# d = dict([('jan', 1), ('feb', 2), ('march', 3)])
d = dict([('one',1), ('two',[3,3,3,'ff']) ])
print(d['two'][3])

t = (1,2,3,4,5)
print(reversed(list(t)))

for o in reversed(t):
    print(o)