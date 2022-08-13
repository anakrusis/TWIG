# TWIG (Transpiler for Windowed Interactive Graphics)
# started 2022-08-10

# usage: python twig.py [file in] [def] [file out]

import json
import sys

from identifier import Identifier

keywords = ["class","extends","false","for","function","if","return","true","while"]
lonetokens = ["{","}","(",")","#",";","."]

identifiers = {};

def tokenize(lines):
    tokens = [];
    # first splitting up tokens by spaces and line breaks in the default fashion    
    for line in lines:
        tokens.extend( line.split() );
        tokens.append("\n")

    # and now all the special characters which get a token of their own
    for tind in range(len(tokens)-1, -1, -1):
        t = tokens[tind]
        
        for cind in range(len(t)-1, -1, -1):
            c = t[cind];

            #print("t: " + t)
            #print("c: " + c)

            try:
                aind = lonetokens.index(c)
            except:
                pass;
            else:
                before = t[:cind]; #print("before: " + before)
                after = t[cind+1:]; #print("after: " + after)

                tokens.pop(tind)

                tokens.insert(tind, after);
                tokens.insert(tind, c);
                tokens.insert(tind, before);

                t = tokens[tind]

    # removing any blank tokens
    for tind in range(len(tokens)-1, -1, -1):
        t = tokens[tind]
        if t == "":
            tokens.pop(tind);

    #print("\nTokens:")
    #for t in tokens:
        #print(t)

    return tokens;

def exitWithError(line, message):
    sys.exit(message + " on line " + str(line))

# Identifiers are the user defined names of things
def isIdentifier(token):
    try:
        keyind = keywords.index(token)
    except:
        pass;
    else:
        return False

    try:
        ltind = lonetokens.index(token)
    except:
        return True
    else:
        return False

def parseTokens(tokens):
    # list of what objects we are currently in from shallow to deep
    # I might make this list contain both the name and starting index of the object, and possibly more info like type
    tree = [];
    # for skipping over tokens if they dont need to be handled, or were previously handled
    skipcounter = 0;
    # list of user-defined things
    identifiers = {};

    currentline = 1;

    for tind in range(0, len(tokens)):
        if skipcounter > 0:
            skipcounter -= 1;
            continue;
        
        t = tokens[tind];        
        nind = tind + 1;

        if t == "\n":
            currentline += 1; continue;

        print(t)
        
        if t == "class":
            if nind >= len(tokens):
                exitWithError(currentline, "Syntax error: no name for class")
            
            nt = tokens[nind];
            if not isIdentifier(nt):
                exitWithError(currentline, "Syntax error: invalid class name")
                
            ident = Identifier(nt, "class"); identifiers[nt] = ident;
    
    return;

def parseDefinitions():
    return;

def main():
    args = sys.argv
    arglength = len(args);
    if arglength != 4:
        print("\nWrong number of argmuents. Usage: \npython twig.py [file in] [def] [file out]")
        return;

    # loading the definitions of the target language
    defs_file = open( "def/" + args[2], "r" );
    defs = json.loads(defs_file.read())
    defs_file.close();

    # now loading up the input file to be parsed
    in_file = open( "in/" + args[1], "r" );
    in_lines = in_file.readlines();
    in_file.close();

    in_tokens = tokenize(in_lines);
    parseTokens(in_tokens);

main();
