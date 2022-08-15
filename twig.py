# TWIG (Transpiler for Windowed Interactive Graphics)
# started 2022-08-10

# usage: python twig.py [file in] [def]

import json
import sys

from identifier import Identifier

keywords = ["class","extends","false","for","function","if","return","true","while"]
lonetokens = ["{","}","(",")","#",";",".","=","+","-","*","/","\""]

identifiers = {};

def tokenize(lines):
    tokens = [];
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

def translateTokens(tokens):
    # list of what objects we are currently in from shallow to deep
    # I might make this list contain both the name and starting index of the object, and possibly more info like type
    tree = [];
    # for skipping over tokens if they dont need to be handled, or were previously handled
    skipcounter = 0;
    # list of user-defined things
    identifiers = {};

    outtokens = [];

    currentline = 1;
    # what token index in outtokens to insert stuff at
    cursor = 0;

    for tind in range(0, len(tokens)):
        if skipcounter > 0:
            skipcounter -= 1;
            continue;
        
        t = tokens[tind];        
        nind = tind + 1;

        if t == "\n":
            currentline += 1; continue;

        #print(t)

        #if t == "}":
            #tree.pop();
        
        if t == "class":
            if nind >= len(tokens):
                exitWithError(currentline, "Syntax error: no name for class")

            # the next token will be the name of the class
            nt = tokens[nind];
            if not isIdentifier(nt):
                exitWithError(currentline, "Syntax error: invalid class name")
                
            ident = Identifier(nt, "class"); identifiers[nt] = ident;
            skipcounter += 1;

            # the next next token could be "extends"...
            nnind = nind + 1;
            if nnind < len(tokens):
                nnt = tokens[nnind];
                if nnt == "extends":

                    # ...then the next next next token would be the name of the parent class.
                    nnnind = nnind + 1;
                    if nnnind < len(tokens):
                        nnnt = tokens[nnnind];
                        ident.parentname = nnnt;
                        
                        skipcounter += 2;

            tree.append( ident );

            # now that we know the class name, parent name (if present) and more
            # we can piece together the outer skeleton of the class, and leave space to put the inner code inside
            classform = defs["class"]["form"];

            bodystart = -1;

            # Todo make this a function and also parse conditionals before adding
            for formline in classform:
                cl = formline.replace("@N", ident.name);
                cl = cl.replace("@S", ident.parentname);

                if formline == "@B":
                    bodystart = cursor;
                
                outtokens.insert(cursor, cl);
                cursor += 1;

            if bodystart == -1:
                exitWithError(currentline, "Syntax error: class form has no body")

            cursor = bodystart;
            # the @B must be removed so the inner code can go there instead
            outtokens.pop(cursor);

            continue;

        if t == "function":
            if nind >= len(tokens):
                exitWithError(currentline, "Syntax error: no name for function")
                
            # the next token will be the name of the function
            nt = tokens[nind];
            if not isIdentifier(nt):
                exitWithError(currentline, "Syntax error: invalid function name")
            
            ident = Identifier(nt, "function"); identifiers[nt] = ident;
            skipcounter += 1;

            funcform = defs["function"]["form"];

            # if this function is directly inside a class definition, and the function name is the same as the class name
            # then this is a constructor, and it has the ability to be formatted differently from other funcs
            if len(tree) > 0:
                treetop = tree[-1]; treetoptype = treetop.itype
                if treetoptype == "class" and nt == treetop.name:
                    funcform = defs["class"]["constructor"]["form"];

            tree.append( ident );

            # now the parameters of the function must be gotted so they can be passed to the @P section

            print(funcform)
            
    return outtokens;

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
    global defs
    defs = json.loads(defs_file.read())
    defs = parseDefinitions(defs);
    defs_file.close();

    # now loading up the input file to be parsed
    in_file = open( "in/" + args[1], "r" );
    in_lines = in_file.readlines();
    in_file.close();

    in_tokens = tokenize(in_lines);
    out_tokens = translateTokens(in_tokens);

    out_filename = args[1].replace(".twig", defs["fileextension"]);
    out_file = open( "out/" + out_filename, "w");
    for token in out_tokens:
        out_file.write(token);
    out_file.close();

main();
