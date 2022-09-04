from identifier import Identifier
import lexer as Lexer

# encapsulates the internal state of the translation process
# This is intended to avoid global variables sillyness
class Translator:
    def __init__(self):
        # the current index at which we are inserting/appending tokens to outtokens
        self.cursor = 0;
        # list of all user defined things in the code
        self.identifiers = {};
        
        # output to file
        self.outtokens = [];

    # This is the main translation function below.
    def translateTokens(self, tokens, defs):
        # list of what objects we are currently in from shallow to deep
        # I might make this list contain both the name and starting index of the object, and possibly more info like type
        tree = [];
        # for skipping over tokens if they dont need to be handled, or were previously handled
        skipcounter = 0;

        self.identifiers = {};
        self.outtokens = [];

        # counts the lines of text as they appear in the initially inputted code 
        # so this line can be told back to the user in error messages
        inputtextline = 1;
        # what token index in outtokens to insert stuff at
        self.cursor = 0;

        for tind in range(0, len(tokens)):
            if skipcounter > 0:
                skipcounter -= 1;
                continue;
            
            t = tokens[tind];        
            nind = tind + 1;

            if t == "\n":
                inputtextline += 1; continue;
            
            if t == "class":
                if nind >= len(tokens):
                    exitWithError(inputtextline, "Syntax error: no name for class")

                # the next token will be the name of the class
                nt = tokens[nind];
                if not Lexer.isIdentifier(nt):
                    exitWithError(inputtextline, "Syntax error: invalid class name")
                    
                ident = Identifier(nt, "class"); self.identifiers[nt] = ident;
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
                            ident.supername = nnnt;
                            
                            skipcounter += 2;

                tree.append( ident );

                # now that we know the class name, parent name (if present) and more
                # we can piece together the outer skeleton of the class, and leave space to put the inner code inside
                classform = defs["class"]["form"];

                # a table is made which contains all the replacement of control codes here:
                replacetable = {
                    "@N": ident.name,
                    "@S": ident.supername
                }

                self.generateFromForm(classform, replacetable)

                continue;

            if t == "function":
                if nind >= len(tokens):
                    exitWithError(inputtextline, "Syntax error: no name for function")
                    
                # the next token will be the name of the function
                nt = tokens[nind];
                if not Lexer.isIdentifier(nt):
                    exitWithError(inputtextline, "Syntax error: invalid function name")
                
                ident = Identifier(nt, "function"); self.identifiers[nt] = ident;
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
                
                # the next identifier will have to be open parenthesis, and then a list of parameters will be seperated by commas
                # and finally this list will be terminated with close parenthesis

                print(funcform)
                
        return self.outtokens;

    # generates a structure like a class or a function given a table of replacements
    def generateFromForm(self, classform, replacetable):
        bodystart = -1;

        # Todo parse conditionals before adding
        for formline in classform:
            cl = formline;
            for key in replacetable:
                cl = cl.replace(key, replacetable[key]);

            if formline == "@B":
                bodystart = self.cursor;
            
            self.outtokens.insert(self.cursor, cl);
            self.cursor += 1;

        if bodystart == -1:
            exitWithError(currentline, "Syntax error: class form has no body")

        cursor = bodystart;
        # the @B must be removed so the inner code can go there instead
        self.outtokens.pop(cursor);
