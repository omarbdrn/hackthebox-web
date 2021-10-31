import sys
import json
import re

class RE:
    def __init__(self):
        # Redacted for now, going to add the linkFunction, getRelations methods and going to update definitives for better reversing
        self.definitives = {"redacted": [], "redacted": {}, "redacted": "redacted", "redacted": "redacted"}
        self.padding = 7
        self.RegexS = {"(?<=com)(.*?)(?=\")": "com", "(?<=bk)(.*?)(?=\,|\))": "bk"}
        self.msgPad = " "*self.padding
        self.functions = []

    def json_extract(self, obj, key):
        """If it works don't touch it"""
        arr = []

        def extract(obj, arr, key):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    # updated it to one character for redaction
                    if str(v).strip()[0:1] == "(":
                        self.splitFunctions(v)
                    if isinstance(v, (dict, list)):
                        extract(v, arr, key)
            elif isinstance(obj, list):
                for item in obj:
                    extract(item, arr, key)
            return arr

        values = extract(obj, arr, key)
        return values
    
    def checkFunction(self, function, i):
        # Useless, going to be removed
        try:
            if function.split(i)[1][0] == ".":
                i = i+"."+re.findall("[a-zA-Z0-9_-]*", function.split(i)[1].split(".")[1])
            i = self.checkFunction(i)
            return i
        except:
            return i
    
    def splitFunctions(self, function):
        for rgx in self.RegexS:
            start = self.RegexS[rgx]
            output = re.findall(rgx, function)
            for i in output:
                i = start+i
                i = self.checkFunction(function, i)
                if i not in self.functions:
                    self.functions.append(i)

    def readFile(self, filename):
        content = open(filename,"r")
        content = content.readlines()
        for line in content:
            line = line.strip()
            jObject = json.loads(line)
            self.json_extract(jObject, "core")
        for function in self.functions:
            print(function)

ref = RE()
if len(sys.argv) > 1:
    ref.readFile(sys.argv[1])
else:
    print("python3 understand.py payload.txt")
