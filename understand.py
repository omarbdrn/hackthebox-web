import sys
import json
import re
import inspect
import time

class bloks:
    def __init__(self):
        self.types = {"i32":int, "f32":float, "bool":bool, "string":str, "map":dict, "array":list}
        self.typeC = {"i32":"int replace = 1;", "f32":"float replace = 0.1;", "bool":"bool replace = true; // demo values", "string":"string replace = \"Demo\";", "map":"dict replace = {\"map\" => \"test\"};", "array":"char replace[10];", "one_tap_login":"token"}
        self.header = "int main() {"
        self.footer = "};"
        self.code = self.header+"\n"
        self.tab = " "*4

    def automate_login(self, nonce, token, signature):
        """ Redacted for the new update """
        return 0

    def construct(report, line):
        """ Constructing Python Code ( Assigned API v8.0 instead of obfuscated-v13.0 )"""
        return 0

    def report(self, line):
        self.code += self.tab+line+"\n"

    class action:
        """ Actions Class """
        def execute(self, ftype, frest):
            if ftype in self.typeC:
                self.report(self.typeC[ftype].replace("replace", "demo"))
            
class RE:
    def __init__(self):
        self.definitives = {"api": 5, "path": "redacted", "cookie": "redacted", "headers": "redacted"}
        self.padding = 7
        self.RegexS = {"(?<=com)(.*?)(?=\")": "com", "(?<=bk)(.*?)(?=\,|\))": "bk"}
        self.msgPad = " "*self.padding
        self.functions = []

    def getValue(self, function=None, content=None, caller=None, value=None):
        if caller == "extract":
            if isinstance(value, str):
                # It will be hard to get start and end of each function since their is multi level inner functions
                pass
        if caller == "readFile":
            if content != None:
                for line in content:
                    line = line.strip()
                    jObject = json.loads(line)
                    self.json_extract(jObject, function, inspect.stack()[0][0].f_code.co_name)


    def json_extract(self, obj, key, caller):
        """Recursively fetch values from nested JSON."""
        arr = []

        def extract(obj, arr, key, caller):
            """Recursively search for values of key in JSON tree."""
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if caller == "getValue":
                        self.getValue(function=key, value=v, caller=inspect.stack()[0][0].f_code.co_name)
                    if str(v).strip()[0:1] == "(":
                        self.splitFunctions(v)
                    if isinstance(v, (dict, list)):
                        extract(v, arr, key, caller)
            elif isinstance(obj, list):
                for item in obj:
                    extract(item, arr, key, caller)
            return arr

        values = extract(obj, arr, key, caller)
        return values
    
    def checkFunction(self, function, i):
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
                i = i.replace("\"", "")
                if i not in self.functions:
                    self.functions.append(i)

    def readFile(self, filename):
        content = open(filename,"r")
        content = content.readlines()
        for line in content:
            line = line.strip()
            jObject = json.loads(line)
            self.json_extract(jObject, "", inspect.stack()[0][0].f_code.co_name)
        for function in self.functions:
            if "bk.action" in function:
                # self.getValue(function, content, inspect.stack()[0][0].f_code.co_name)
                bk.action.execute(bk, function.split(".")[2], function)
        bk.code += bk.footer
        print(bk.code)

ref = RE()
bk = bloks()
if len(sys.argv) > 1:
    ref.readFile(sys.argv[1])
else:
    print("python3 understand.py payload.txt")
