from cache import Cache

def basicVisualTests():
    c = Cache()
    c.add(1,56)
    c.add(3,59)
    c.add(39,1159)

    c.writeToDisk()

    print(c.head)
    print(c.head.next)
    print(c.head.next.next)

    print(c.writeToDisk())
    print(c.get(1))

    print(c.writeToDisk())
    print(c.get(6546))
    print(c.writeToDisk())

    c.add(6546, "testing")
    print(c.writeToDisk())
    print(c.get(39))
    print(c.writeToDisk())

    print("Testing overflow")
    print(c.getCacheValues())

    for i in range(0,12):
        c.add(i, "%s : %s" % (i, i+7))
        print(c.getCacheValues())
        
    print(c.getCacheValues())
    
#Tests if overflow works properly.
def testOverflow():
    c = Cache(cacheSize=5)
    for i in range(0,6):
        c.add(i, i)
    if c.get(0) is not None:
        print("Failed to overflow correctly, the oldest entry is still in cache.")
        print(c.getCacheValues())
        return
    if c.get(1) is None:
        print("We overflowed too much.")
        print(c.getCacheValues())
        return
    c.add(6,6)
    
    #Test to make sure that we moved 1 to be near the front and not the tail
    #since we used .get(1) right before the add(6)
    if c.get(1) is None:
        print("We deleted a recently accessed entry.")
        print(c.getCacheValues())
        return
    
    if c.get(2) is not None or c.get(6) is None:
        print("We failed to overflow correctly and remove an entry.")
        print(c.getCacheValues())
        return 
    
    print("Passed the overflow tests.")
    
#Tests if the cache can be written to and read from disk correctly.
def writeReadTest():
    c = Cache()
    for i in range(0,5):
        c.add(i, str(i))
    oldValues = c.getCacheValues()
    c.writeToDisk()
    
    c = Cache()
    c.loadFromDisk()
    newValues = c.getCacheValues()
    if newValues[0] != oldValues[0] or newValues[1] != oldValues[1]:
        print("Reloading values differ from original.")
        print("Old values:")
        print(oldValues)
        
        print("New values:")
        print(newValues)
    else:
        print("Write Read test successful")
        
#Tests if elements of the cache can be deleted correctly.
def deleteTest():
    c = Cache()
    c.add(1, "one")
    c.add('h', "letter h")
    c.add('12', "twelve")
    c.expire(1)
    if c.get(1) is not None:
        print("deletion of 1 failed")
        print(c.getCacheValues())
        
    c.expireAll()
    y = c.getCacheValues()
    for entry in y: 
        if entry: 
            print('failed to delete all.')
            break
    else:
        print("Successfully deleted all entries.")

    #We cache some numbers, note that 0 will be the "least recently used" member
    #of the cache. 
    for i in range(0,10):
        c.add(i, i)
    
    #We remove the tail
    c.expire(0)
    #We remove the head
    c.expire(9)
    #We remove a number in the middle.
    c.expire(5)
    
    values = c.getCacheValues()[1]
    expectedValues = list(range(8,0,-1))
    if values != expectedValues:
        print('values and expected values dont match')
        print('cache ', values)
        print('expected ', expectedValues)
    
    reversedValues = [x.key for x in c.reverse_iterate()]
    # print('F---------R')
    # print(values)
    # print(reversedValues)
    # print('-----------')
    reversedValues.reverse()
    if values != reversedValues:
        print("Forward and reverse don't match")
        print('cache forward', values)
        print('cache reverse ', reversedValues)
    else:
        print("Tested forward and reverse values and they match.")
        
    #make sure we can add in new things still.
    c.add(1, "one again")
    c.add(11, "eleven")
    
    if c.get(1) is None or c.get(11) is None:
        print("adding new values after deletion failed")
    else:
        print("Successfully able to add new values after deletion.")
    
#Tests if cache elements expire when expected to.
def timerTest():
    print("Testing the timed expiry of elements.")
    
    import time
    
    c = Cache(expiryTime=4)
    c.add(1, "one threading")
    print("Sleeping for 3 seconds.")
    
    time.sleep(3)
    c.add(2, "two")
    c.add(3, "two")
    print("Sleeping for 2 seconds.")
    time.sleep(2)
    
    #We should not be seeing 1 here.
    #print(c.getCacheValues())
    if c.get(1) is not None:
        print("timer test for key 1 failed.")
    else:
        print("Successfully removed key 1 after its time expired.")
    if c.get(2) is None or c.get(3) is None:
        print("timer test for keys 2 or 3 failed as they expired too early.")
    
    print("Sleeping for 3 seconds")
    time.sleep(3)
    
    if c.get(2) is not None or c.get(3) is not None:
        print("timer test for 2&3 failed")
    else:
        print("Keys 2 and 3 also expired as expected.")
    
    #We check if stopping then restarting the timer works
    #as expected.
    print("Testing if stopping the timer removes nothing.")
    c.add(4, "four")
    c.stopTimer()
    print("Sleeping for 6 seconds.")
    time.sleep(6)
    
    if c.get(4) is None:
        print("Failure: timer deleted key 4 when it was turned off.") 
    else:
        print("Stopping the timer successful")
        
    print("Restarting timer and sleeping for 2 seconds.")
    c.restartTimer()
    time.sleep(2)
    
    if c.get(4) is not None:
        print("Failure: timer did not delete key 4 when it was restarted.") 
    else:
        print("Restarting the timer successful")
    
    print("Testing if post restart the timer can also stop properly when desired.")
    c.add(5, "five")
    c.stopTimer()
    print("Sleeping for 6 seconds.")
    time.sleep(6)
    
    if c.get(5) is None:
        print("Failure: timer deleted key 5 when it was turned off.") 
    else:
        print("Stopping the timer successful")
    
    
if __name__ == "__main__":
    testOverflow()
    writeReadTest()
    deleteTest()
    timerTest()