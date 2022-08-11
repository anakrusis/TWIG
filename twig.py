# TWIG (Transpiler for Windowed Interactive Graphics)
# started 2022-08-10

# usage: python twig.py [file in] [def] [file out]

import json
import sys

keywords = ["class","for","function","if","return","while"]
lonetokens = ["{","}","(",")","#"]

def tokenize(lines):
    tokens = [];
    # first splitting up tokens by spaces in the default fashion    
    for line in lines:
        tokens.extend( line.split() );

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

    print("\nTokens:")
    for t in tokens:
        print(t)

    return tokens;


def parseTokens(tokens):
    # list of what objects we are currently in from shallow to deep
    # I might make this list contain both the name and starting index of the object, and possibly more info like type
    tree = [];
    # for skipping over tokens if they dont need to be handled, or were previously handled
    skipcounter = 0;

    for tind in range(0, len(tokens)):
        if skipcounter > 0:
            skipcounter -= 1;
            continue;
        
        t = tokens[tind];   
    
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
