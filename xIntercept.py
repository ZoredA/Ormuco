import sys

"""this checks if two coordinates on the x-axis intercept.
    Check tests() for seeing how this works in code or run this file
    to get the user prompts.
    checkIfOverlap is the function we call and use. 
"""

def checkIfOverlap(co_ord1, co_ord2):

    #We change the coordinates to make sure the first number is 
    #smaller than the second. Basically changing the direction of the line 
    #if required.
    #Direction is irrelevant to overlap. 
    if co_ord1[1] < co_ord1[0]:
        co_ord1 = (co_ord1[1], co_ord1[0])
    if co_ord2[1] < co_ord2[0]:
        co_ord2 = (co_ord2[1], co_ord2[0])

    #We assume the coordinates 
    #We satisfie the condition that the 2nd numbers
    #in each coordinate is greater than the first.
    #e.g. for (x1,x2) (x3, x4)
    # x2 > x1 and x4 > x3

    #The cases to cover
    # no overlap 
    if co_ord2[0] > co_ord1[1]:
        return False
    if co_ord1[0] > co_ord2[1]:
        return False
    if co_ord2[0] >= co_ord1[0] and co_ord2[0] <= co_ord1[1]:
            return True 
    if co_ord1[0] >= co_ord2[0] and co_ord1[0] <= co_ord2[1]:
            return True 
    print("Ran into a missing case. Should not happen.")
    return True 

def tests():
    testList = [
    
    {#no overlap test
        'one' : (1,3),
        'two' : (4,5),
        'expected' : False
    },
    
    {#overlap test
        'one' : (1,4),
        'two' : (3,5),
        'expected' : True
    },
    
    {#complete overlap test
        'one' : (4,5),
        'two' : (4,5),
        'expected' : True
    },
    
    {#complete overlap test reversed
        'one' : (4,5),
        'two' : (5,4),
        'expected' : True
    },
    
    {#negative with overlap 
        'one' : (-4,5),
        'two' : (-2,6),
        'expected' : True
    },
    
    {#negative with no overlap 
        'one' : (-4,-5),
        'two' : (-2,6),
        'expected' : False
    },
    
    ]
    for test in testList:
        print("got %s" % checkIfOverlap(test['one'], test['two']) + " expected %s" % test['expected'])
    
    
if __name__ == "__main__":
    #Assume the input is comma delimited
    user_input = input('Enter 4 numbers, separated by commas: ')
    user_input = user_input.strip().split(',')
    if len(user_input) != 4 or '' in user_input:
        print("Please enter 4 numbers separated by commas")
        sys.exit(0)
    
    co_ord1 = (int(user_input[0]), int(user_input[1]))
    co_ord2 = (int(user_input[2]), int(user_input[3]))
    
    print(checkIfOverlap(co_ord1, co_ord2))