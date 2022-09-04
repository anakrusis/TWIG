# TWIG (Transpiler for Windowed Interactive Graphics)
# started 2022-08-10

# usage: python twig.py [file in] [def]

import json
import sys

import lexer as Lexer
from identifier import Identifier
from translator import Translator

keywords = ["class","extends","false","for","function","if","return","true","while"]
lonetokens = ["{","}","(",")","#",";",".","=","+","-","*","/","\""]

def tokenize(lines):
    tokens = [];

    # todo: string literal must not be split up into multiple tokens (because the space separation damages the strings)
    
    # first splitting up tokens by spaces and line breaks in the default fashion    
    for line in lines:
        tokens.extend( line.split() );
        tokens.append("\n")

    # and now all the special characters which get a token of their own
    for i in range( 0, len(lonetokens) ):
        seperateTokens( tokens, lonetokens[i] );

    print("\nTokens:")
    for t in tokens:
        print(t)

    return tokens;

def exitWithError(line, message):
    sys.exit(message + " on line " + str(line))

# iterates backwards, upon finding matching character sequence, it splits one string into three:
# the part before, the sequence itself, and the part after
def seperateTokens(tokenlist, lonetoken):
    for i in range(len(tokenlist)-1, -1, -1):     
        bind = 1;
        while bind != -1:
            bind = tokenlist[i].rfind(lonetoken)
            if bind == -1: break
                    
            before = tokenlist[i][:bind];
            after = tokenlist[i][bind + len(lonetoken):];

            tokenlist.pop(i)
            tokenlist.insert(i, after)
            tokenlist.insert(i, lonetoken)
            tokenlist.insert(i, before)

    # removing any blank tokens
    for tind in range(len(tokenlist)-1, -1, -1):
        t = tokenlist[tind]
        if t == "":
            tokenlist.pop(tind);

def seperateTokensInDict( dic ):
    for k, v in dic.items():
        if type(v) is dict:
            seperateTokensInDict(v)
            
        if k == "form":
            # the sequences @B and @P are seperated into their own tokens
            seperateTokens(v, "@B");
            seperateTokens(v, "@P");       

def parseDefinitions(defs):

    # Tokens like @B and @P, which will have stuff inserted at their position, are seperated so that
    # their indices will be useful and simple to deal with later on in the transpilation
    seperateTokensInDict(defs)
    
    return defs;

def main():
    args = sys.argv
    arglength = len(args);
    if arglength != 3:
        print("\nWrong number of argmuents. Usage: \npython twig.py [file in] [def]")
        return;

    # loading the definitions of the target language
    defs_file = open( "def/" + args[2], "r" );
    defs = json.loads(defs_file.read())
    defs = parseDefinitions(defs);
    defs_file.close();

    # now loading up the input file to be parsed
    in_file = open( "in/" + args[1], "r" );
    in_lines = in_file.readlines();
    in_file.close();

    translator = Translator();
    in_tokens = tokenize(in_lines);
    out_tokens = translator.translateTokens(in_tokens, defs);

    out_filename = args[1].replace(".twig", defs["fileextension"]);
    out_file = open( "out/" + out_filename, "w");
    for token in out_tokens:
        out_file.write(token);
    out_file.close();

main();
