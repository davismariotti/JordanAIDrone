import operator


my_list = [0, 0, 1]

index = max(enumerate(my_list), key=operator.itemgetter(1))[0]

print(index)