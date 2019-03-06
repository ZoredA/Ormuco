#Requirements:
#Least Recently Used Cache 
#Time Expiry
#Real time writes, resilience against crashes
#Flexible schema
#Cache can expire 

import json 
import os 
import datetime
from threading import Thread, Event 

class CacheEntry():
    """
        Internal class that keeps track of linked list entries.
        Can be accessed externally but generally not needed 
    """
    def __init__(self, key, previous, next, duration):
        self.key = key
        self.previous = previous 
        self.next = next 
        self.creationTime = datetime.datetime.utcnow()
        if duration:
            self.expiryTime = self.creationTime + datetime.timedelta(seconds=duration)
        else:
            #If we don't have expiry times enabled, we just set our expiry time to be 
            #the maximum possible time. 
            self.expiryTime = datetime.datetime.max 
        
       
#Threading Reference:
#https://stackoverflow.com/a/12435256
#This thread is just a timer that checks the cache every second or so
#and removes any entries that have gone past their expiry time. 
class _CacheThread(Thread):
    """
        Cache threading helper class. Expires entry when their time is past.
    """
    def __init__(self, event, cache):
        Thread.__init__(self)
        self.stopped = event
        self.cache = cache
        
    #We run this timer thread with a roughly 1 second interval. 
    def run(self):
        while not self.stopped.wait(1.0):
            for entry in self.cache.iterate():
                if entry.expiryTime <= datetime.datetime.utcnow():
                    self.cache.expire(entry.key)

class Cache():

    #Cache size is number of objects to store. 
    #Expiry Time is in seconds. If none, items don't expire 
    #but get removed once the cache fills up. 
    def __init__(self, cacheSize=10, expiryTime=None, fileName="cache.json"):
        """
            The main class. Can be initialized like so
            from cache import Cache
            c = Cache()
            cacheSize is the number of elements the cache stores before 
            removing the oldest one to make space. 
            expiryTime is in seconds and once it is past, elements are deleted
            (note: exact time accuracy can't be guaranteed, but expired entries should
            be removed within a second or two of their expiry time.)
            fileName is the persistent file the cache stores the data in 
            on disk. By default this is never written to, but any time 
            the external cache user can call Cache.WriteToDisk(), Cache.loadFromDisk()
            can be used to reload cached values. 
            
            This cache does not auto retrieve any non present values. It just returns None.
            External code can catch this and act accordingly
            value = cache.get(key)
            if value is None:
                value = REMOTE_CALL(key)
                cache.add(key, value)
                
            test.py
        """
    
    
        self.size = cacheSize
        self.duration = expiryTime
        self.fileName = fileName
        
        #We use a dictionary to contain the actual data values 
        #We can return elements if their key is passed in 
        self.elements = {}
        
        #We use a linked list to keep track of the order of elements 
        #in the cache. Original idea inspired by this 
        #article https://medium.com/@krishankantsinghal/my-first-blog-on-medium-583159139237
        self.head = None 
        self.tail = None 
        
        #this is for tracking the linked list entries 
        self.entries = {}
        
        if expiryTime:
            self.stopSignal = Event()
            self.timer = _CacheThread(self.stopSignal, self)
            self.timer.daemon = True
            self.timer.start()
        
    def stopTimer(self):
        if self.duration is not None:
            self.stopSignal.set()

    def restartTimer(self):
        if self.duration is not None:
            self.stopSignal = Event()
            self.timer = _CacheThread(self.stopSignal, self)
            self.timer.daemon = True
            self.timer.start()
        
    def add(self, key, value):
        self.elements[key] = value 
        self.updateLatest(key)
        if len(self.elements) > self.size:
            #We remove the tail i.e. the oldest entry in the cache. 
            self.elements.pop(self.tail.key)
            self.entries.pop(self.tail.key)
            
            self.tail.previous.next = None
            self.tail = self.tail.previous 
        return self 
        
    def get(self, key):
        if key in self.elements:
            self.updateLatest(key)
            return self.elements[key]
        else:
            return None
            
    #removes a key from the cache. 
    def expire(self, key):
        self.elements.pop(key)
        self.entries.pop(key)
        
        if self.head.key == key:
            self.head = self.head.next
            if self.head is not None:
                self.head.previous = None
        if self.tail.key == key:
            self.tail = self.tail.previous 
            if self.tail is not None:
                self.tail.next = None
        
    def expireAll(self):
        self.elements = {}
        self.entries = {}
        self.head = None 
        self.tail = None 
        
    def updateLatest(self, key):
        #We change the position of the head to be whatever was passed in. 
        #If we don't have a head, i.e. the cache is empty, we just set it.
        if self.head is None:
            self.head = CacheEntry(key, None, None, self.duration)
            self.tail = self.head
            self.entries[key] = self.head
            return
        
        if self.head.key == key:
            return 
        
        if key not in self.entries:
            newEntry = CacheEntry(key=key, previous=None, next=self.head, duration=self.duration)
            self.head.previous = newEntry
            self.entries[key] = newEntry
            self.head = newEntry
            return
        
        entry = self.entries[key]
        if entry.next:
            entry.next.previous = entry.previous 
        else:
            #We are the tail so we set our tail to be the previous one.
            self.tail = entry.previous 
            
        #Note: We know there is a previous because we are not the head 
        entry.previous.next = entry.next 
        
        self.head.previous = entry
        entry.next = self.head
        self.head = entry
        
    #Returns the cache and the order they are stored 
    #in as a tuple of the dictionary and a list for the order.
    #Mostly used for testing.
    def getCacheValues(self):
        cache_order = [entry.key for entry in self.iterate()]
        
        return (self.elements, cache_order, 
            None if not self.head else self.head.key, 
            None if not self.tail else self.tail.key)
        
    #We write the entire cache to disk.
    #Note: We assume the values being stored are json compliant,
    #if this assumption is false, we can implement a custom serializer, use pickle or 
    #some other method of making the data serializable
    #Note 2: JSON has restrictions on object keys that python
    #dictionaries don't have (e.g. keys are always strings in json)
    #so to try and increase what we can have as keys, we are 
    #going to store our cache dictionary 
    #as two arrays of keys and values. 
    def writeToDisk(self):
        #We write the cache to a temporary file.
        temp_file = self.fileName + "_tmp"
        perm_file = self.fileName
        
        cache_in_order = [entry.key for entry in self.iterate()]
        values = [self.elements[key] for key in cache_in_order]
        backup = {
            'keys': cache_in_order,
            'values': values
        }
        
        with open(temp_file, "w") as f:
            json.dump(backup, f)
            
        #We try to rename the tmp file. 
        try:
            os.rename(temp_file, perm_file)
        except OSError:
            #The file already exists
            #note: this operation is not atomic
            os.remove(perm_file)
            os.rename(temp_file, perm_file)
            
        return (self.elements, cache_in_order)
        
    #A python generator that 
    #iterates through the nodes and yields each one.
    def iterate(self):
        if self.head is None:
            return None 
        current = self.head
            
        while current.next is not None:
            yield current 
            current = current.next 
        
        yield current
        
    #the same as above but in reverse. 
    def reverse_iterate(self):
        if self.tail is None:
            return None 
        current = self.tail
        
        while current.previous is not None:
            yield current
            current = current.previous
            
        yield current
        
    def loadFromDisk(self):
        persistent_file = self.fileName
        
        with open(persistent_file, 'r') as f:
            #We load up a file in case we crashed or what have you.
            data = json.load(f)
            
        self.elements = dict(zip(data['keys'], data['values']))
            
        #To recreate the order and the entries, we simply reverse the read array
        #and call update on each element. This is akin to accessing each element in the cache   
        for key in reversed(data['keys']):
            self.updateLatest(key)
        