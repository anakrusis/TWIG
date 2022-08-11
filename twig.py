# TWIG (Transpiler for Windowed Interactive Graphics)
# started 2022-08-10

# usage: python twig.py [file in] [def] [file out]

import json
import sys

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

    in_tokens = [];

    # first splitting up tokens by spaces in the default fashion    
    for line in in_lines:
        in_tokens.extend( line.split() );

    # and now all the characters which get a token of their own
    alonetokens = ["{","}","(",")","#"];

    for tind in range(len(in_tokens)-1, -1, -1):
        t = in_tokens[tind]
        
        for cind in range(len(t)-1, -1, -1):
            c = t[cind]; print(c)

            try:
                aind = alonetokens.index(c)
            except:
                pass;
            else:
                before = t[:cind+1]; print("before: " + before)
                after = t[cind+1:]; print("after: " + after)
                
                in_tokens[tind - 1] = before;
        

    print("\nTokens:")
    for t in in_tokens:
        print(t)
            
    
    #print("\n" + in_lines);

main();
