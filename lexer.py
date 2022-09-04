# The lexer handles seperating apart tokens and categorizing them.
# It doesn't need an internal state, so its functions are not part of a class

# anything that is not a reserved keyword or a lone token is assumed to be an identifier 
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