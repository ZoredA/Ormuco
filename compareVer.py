"""
    This comparator tries to compare two versions (passed in as strings)
    For use outside this file, you would call compareVersions(v1, v2)
    Assumptions:
        -We are only dealing with integers (or floats that can be separated into integers)
        -We are using numbers and not representing say 1.1 as one.one
        -We generally ignore any non numeric characters present in the label (but as a 
        last resort do fallback to string length if the numbers are the same e.g. 1.2 loses to 1.2rev)
    If we don't have an answer, the function returns None.
    See tests() for sample formats we can compare.
"""
import re 

intFinder = re.compile("\d+")
    
#helper function that tries to extract ints.
def extractInt(s):
    return intFinder.findall(s)
    
#We attempt to extract integers from the version
#string and we support a wide number of separators (called delimiters here)
def extractInts(label):
    delimiters = [',',':','-','_']
    delimiter = ''
    for d in delimiters:
        if d in label:
            delimiter = d
            break
    if not d:
        ints = extractInt(label)
        return ints
        
    ints = []
    for s in label.split(d):
        ints += extractInt(s)
    
    return [int(x) for x in ints]
   
def compareVersions(v1, v2):
    v1_integers = extractInts(v1)
    v2_integers = extractInts(v2)
    #our iteration length is the smaller of the two versions.
    length = len(v1_integers) if len(v1_integers) < len(v2_integers) else len(v2_integers)
    bigger = None
    for i in range(0,length):
        if v1_integers[i] == v2_integers[i]:
            continue
        if v1_integers[i] > v2_integers[i]:
            bigger = v1
            break
        else:
            bigger = v2
            break
    if bigger is None:
        if len(v1_integers) > len(v2_integers):
            #They are initially the same, but v1
            #has another revision e.g. 1.3.1 vs 1.3
            bigger = v1
        if len(v2_integers) > len(v1_integers):
            bigger = v2
        #If we have the same number of numbers, but
        #have something else tacked on, we assume it 
        #is text denoting an upgrade e.g. 1.2 and 1.2Revised
        elif len(v1_integers) == len(v2_integers):
            if len(v1.strip()) > len(v2.strip()):
                bigger = v1
            if len(v1.strip()) < len(v2.strip()):
                bigger = v2
            
    return bigger
    
def test():
    test_versions = [
        #v1, v2, the expected answer 
        ('1.2','1.3','1.3'),
        ('1.2.1.1.3','1.3','1.3'),
        ('1.2.1.1.3','1.2.1.1.4','1.2.1.1.4'),
        ('1.2.1.1-3','1.2.1.1-4','1.2.1.1-4'),
        ('1_2','1_3','1_3'),
        ('1_2','1_2rev','1_2rev'),
        ('1_2','1_2', None),
        ('','', None),
        ('','1', '1'),
        ('v1','v2', 'v2'),
        ('v1.4','v2.1', 'v2.1'),
    ]
    
    for index, test in enumerate(test_versions):
        bigger = compareVersions(test[0], test[1])
        print("--------------")
        if bigger == test[2]:
            print("Passed test %s " % index)
        else:
            print("Failed test %s " % index)
        print("Comparison of %s and %s expected to get %s and got" % test + " %s" % bigger) 
        print("**************")
        