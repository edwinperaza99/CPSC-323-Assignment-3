# Used to exit program gracefully 
import time
import sys

# define separators, operators and reserved words
separator = [' ', '\t', ',', ';', '(', ')', '{', '}', '#']
operators = ['+', '-', '*', '/', '=', '<', '>', '<=', '=>', '==', '!=', '!']
keyword = ['if', 'else', 'endif' ,'while', 'function', 'integer', 'bool', 'real', 'ret', 'put', 'get', 'true', 'false']
begin_comment = '[*'
end_comment = '*]'

# define array to store all the words that have been read
words = []

# define dictionary to store tokens
tokens = []

# define current line
current_line = 1

# variables for parser
current_token = None
token_index = 0

# variables for output file
output_file = None

switch = False

# variables for symbol table and assembly code instructions
MEMORY_ADDRESS = 7000
INSTRUCTION_ADDRESS = 1

# Use this variable to store the type to pass to the insert_symbol_table function
LAST_IDENTIFIER_TYPE = None

# define dictionary for symbol table
symbol_table = []
# example of object in symbol table 
# ['Identifier': 'x', 'Memory Location': 7000, 'Type': 'integer']

# define dictionary for assembly code instructions
assembly_code = []
# example of object in assembly code list
# ['Address': 1, 'Operation': 'PUSHI', 'Operand': 0]

# stack for backtrack 
JUMP_STACK = []

# variable to check if we are in declaration list
DECLARATION_LIST = True


# *********************************************************************************************************************************
# ******************************SYMBOL TABLE AND ASSEMBLY CODE STARTS HERE*********************************************************
# *********************************************************************************************************************************
"""All the rules and functions for assignment 3 are here"""
def exit_syntax_analyzer(delay = 10):
    print("\nExiting Syntax Analyzer...")
    print(f"Program will exit in {delay} seconds.")
    time.sleep(delay)
    print("\nSyntax Analyzer Exited.")
    sys.exit(1)


def print_token():
    global current_token, output_file, switch
    if switch == False:
        if current_token['token'] == 'illegal' or current_token['token'] == 'keyword' or current_token['token'] == 'integer' or current_token['token'] == 'real' or current_token['token'] == 'operator':
            print(f"Token: {current_token['token']}\t\t\tLexeme: {current_token['lexeme']}")
            with open(output_file, "a") as file:
                file.write(f"Token: {current_token['token']}\t\t\tLexeme: {current_token['lexeme']}\n")
        else:
            print(f"Token: {current_token['token']}\t\tLexeme: {current_token['lexeme']}")
            with open(output_file, "a") as file:
                file.write(f"Token: {current_token['token']}\t\tLexeme: {current_token['lexeme']}\n")


def print_symbol_table():
    """This function is used to print all the values in the symbol table"""
    global output_file
    print("Symbol Table:")
    print("Memory Location\t\tType\t\tIdentifier")
    for i in symbol_table:
        print(f"{i['Memory Location']}\t\t\t{i['Type']}\t\t{i['Identifier']}")
    print("\n")
    with open(output_file, "a") as file:
        file.write("Symbol Table:\n")
        file.write("Memory Location\t\tType\t\t\tIdentifier\n")
        for i in symbol_table:
            file.write(f"{i['Memory Location']}\t\t\t\t{i['Type']}\t\t\t{i['Identifier']}\n")
        file.write("\n")


def print_assembly_code():
    """This function is used to all the assembly code instructions"""
    global output_file
    print("\nAssembly Code Listing:")
    for i in assembly_code:
        print(f"{i['Address']}\t\t\t{i['Operation']}\t\t\t{i['Operand']}")
    print("\n")
    with open(output_file, "a") as file:
        file.write("\nAssembly Code Listing:\n")
        for i in assembly_code:
            file.write(f"{i['Address']}\t\t\t{i['Operation']}\t\t\t{i['Operand']}\n")
        file.write("\n")


def check_symbol_table(identifier):
    """This function is used to check if the identifier is already in the symbol table"""
    for i in symbol_table:
        if i['Identifier'] == identifier:
            return True
    return False


def insert_symbol_table(identifier):
    """This function is used to insert a new identifier into the symbol table"""
    global symbol_table, MEMORY_ADDRESS, LAST_IDENTIFIER_TYPE, DECLARATION_LIST
    if LAST_IDENTIFIER_TYPE == None:
        print("Error: Identifier type not defined.")
        print("Please define the type of the identifier.")
        with open(output_file, "a") as file:
            file.write("Error: Identifier type not defined.\n")
            file.write("Please define the type of the identifier.\n")
        exit_syntax_analyzer()
    elif LAST_IDENTIFIER_TYPE != 'integer' and LAST_IDENTIFIER_TYPE != 'bool':
        print("Error: Identifier type not valid.")
        print("Please define the type of the identifier. Expected 'integer' or 'bool'")
        with open(output_file, "a") as file:
            file.write("Error: Identifier type not valid.\n")
            file.write("Please define the type of the identifier. Expected 'integer' or 'bool'\n")
        exit_syntax_analyzer()
    if DECLARATION_LIST == True:
        if not check_symbol_table(identifier['lexeme']):
            symbol_table.append({'Identifier': identifier['lexeme'], 'Memory Location': MEMORY_ADDRESS, 'Type': LAST_IDENTIFIER_TYPE})
            MEMORY_ADDRESS += 1
        else:
            print(f"Error: Identifier '{identifier['lexeme']}' already declared at line {identifier['line']}.")
            print("Choose a new unique identifier name.")
            with open(output_file, "a") as file:
                file.write(f"Error: Identifier '{identifier['lexeme']}' already declared at line {identifier['line']}.\n")
                file.write("Choose a new unique identifier name.\n")
            exit_syntax_analyzer()

def get_address(identifier):
    """This function is used to get the memory location of an identifier in the symbol table"""
    for i in symbol_table:
        if i['Identifier'] == identifier:
            return i['Memory Location']
    return None


def back_patch(jump_address):
    """This function is used to back patch the jump instructions"""
    global JUMP_STACK, assembly_code
    address = JUMP_STACK[0]
    JUMP_STACK.pop(0)
    assembly_code[address -1]['Operand'] = jump_address


def push_jumpstack(instruction_address):
    """This function is used to push the instruction address to the jump stack"""
    global JUMP_STACK
    JUMP_STACK.insert(0, instruction_address)


def gen_instruction(operation, operand = None):
    """This function is used to generate assembly code instructions"""
    global assembly_code, INSTRUCTION_ADDRESS
    # Operator      Operand
    # ____________________________________
    # I1) PUSHI     {Integer Value}
    # I2) PUSHM     {Memory Address}
    # I3) POPM      {Memory Address}
    # I4) STDOUT    None
    # I5) STDIN     None
    # I6) ADD       None
    # I7) SUB       None
    # I8) MUL       None
    # I9) DIV       None
    # I10) GRT      None
    # I11) LES      None
    # I12) EQU      None
    # I13) NEQ      None
    # I14) GEQ      None
    # I15) LEQ      None
    # I16) JUMPZ    {Instruction Location} *could be unknown initially*
    # I17) JUMP     {Instruction Location}
    # I18) LABEL    None
    if operand == None:
        assembly_code.append({'Address': INSTRUCTION_ADDRESS, 'Operation': operation, 'Operand': ""})
        INSTRUCTION_ADDRESS += 1
    else:
        assembly_code.append({'Address': INSTRUCTION_ADDRESS, 'Operation': operation, 'Operand': operand})
        INSTRUCTION_ADDRESS += 1

# *********************************************************************************************************************************
# ******************************SYMBOL TABLE AND ASSEMBLY CODE ENDS HERE***********************************************************
# *********************************************************************************************************************************


# *********************************************************************************************************************************
# ******************************SYNTAX ANALYZER CODE STARTS HERE*******************************************************************
# *********************************************************************************************************************************
"""All the rules and functions for the syntax analyzer are here for top down parsing"""
def change_switch():
    global switch
    if switch == False:
        switch = True
    else:
        switch = False

def get_next_token():
    global current_token, token_index, switch
    if token_index < len(tokens):
        current_token = tokens[token_index]
        token_index += 1
    else:
        print("\nReached end of file without parsing errors.\n")
        with open(output_file, "a") as file:
            file.write("\nReached end of file without parsing errors.\n\n")
        switch = True


# Rule 1
# R1) <Rat23F> ::= # <Opt Declaration List> <Statement List> #
def Rat23F():
    global current_token, switch, output_file, DECLARATION_LIST
    get_next_token()
    print_token()
    # print rule
    if switch == False:
        print("\t<Rat23F> ::= # <Opt Declaration List> <Statement List> #")
        with open(output_file, "a") as file:
            file.write("\t<Rat23F> ::=  # <Opt Declaration List> <Statement List> #\n")
    if current_token['lexeme'] == '#':
        get_next_token()
        print_token()
        OptDeclarationList()
        DECLARATION_LIST = False
        StatementList()
        if current_token['lexeme'] == '#':
            get_next_token()
            print_token()
        else:
            print(f"Error: Expected '#' at line {current_token['line']}.")
            print(f"Reading token:", end="")
            with open(output_file, "a") as file:
                file.write(f"Error: Expected '#' at line {current_token['line']}.\n")
                file.write(f"Reading token:")
                print_token()
            exit_syntax_analyzer()
    else: 
        
        print(f"Error: Expected '#' at line {current_token['line']}.")
        print(f"Reading token:", end="")
        with open(output_file, "a") as file:
            file.write(f"Error: Expected '#' at line {current_token['line']}.\n")
            file.write(f"Reading token:")
        print_token()
        exit_syntax_analyzer()


# Rule 10
# R10) <Qualifier> ::= integer | bool 
def Qualifier():
    global current_token, switch, output_file, LAST_IDENTIFIER_TYPE
    if switch == False:
        print("\t<Qualifier> ::= integer | bool")
        with open(output_file, "a") as file:
            file.write("\t<Qualifier> ::= integer | boolean\n")
    if current_token['lexeme'] == 'integer':
        LAST_IDENTIFIER_TYPE = 'integer'
        get_next_token()
        print_token()
    elif current_token['lexeme'] == 'bool':
        LAST_IDENTIFIER_TYPE = 'bool'
        get_next_token()
        print_token()
    # removing reals 
    # elif current_token['lexeme'] == 'real':
    #     get_next_token()
    #     print_token()
    else:
        
        print(f"Error: Expected 'integer' or 'bool' at line {current_token['line']}.")
        print(f"Reading token:", end="")
        with open(output_file, "a") as file:
            file.write(f"Error: Expected 'integer' or 'bool' at line {current_token['line']}.\n")
            file.write(f"Reading token:")
        print_token()
        exit_syntax_analyzer()


# Rule 12
# R12) <Opt Declaration List> ::= <Declaration List> | <Empty>
def OptDeclarationList():
    global current_token, switch, output_file
    if switch == False:
        print("\t<Opt Declaration List> ::= <Declaration List> | <Empty>")
        with open(output_file, "a") as file:
            file.write("\t<Opt Declaration List> ::= <Declaration List> | <Empty>\n")
    DeclarationList()
    Empty()


# Rule 13
# R13) <Declaration List> ::= <Declaration> ; <Declaration List Prime>
def DeclarationList():
    global current_token, switch, output_file
    if switch == False:
        print("\t<Declaration List> ::= <Declaration> ; <Declaration List Prime>")
        with open(output_file, "a") as file:
            file.write("\t<Declaration List> ::= <Declaration> ; <Declaration List Prime>\n")
    Declaration()
    if current_token['lexeme'] == ';':
        get_next_token()
        print_token()
        DeclarationListPrime()
    else:
        
        print(f"Error: Expected ';' at line {current_token['line']}.")
        print(f"Reading token:", end="")
        with open(output_file, "a") as file:
            file.write(f"Error: Expected ';' at line {current_token['line']}.\n")
            file.write(f"Reading token:")
        print_token()
        exit_syntax_analyzer()


# Rule 14
# R14) <Declaration List Prime> ::= <Declaration List> | <Empty>
def DeclarationListPrime():
    global current_token, switch, output_file
    if switch == False:
        print("\t<Declaration List Prime> ::= <Declaration List> | <Empty>")
        with open(output_file, "a") as file:
            file.write("\t<Declaration List Prime> ::= <Declaration List> | <Empty>\n")
    # removing real from here 
    if current_token['lexeme'] == 'integer' or current_token['lexeme'] == 'bool':
        DeclarationList()
    else:
        Empty()


# Rule 15
# R15) <Declaration> ::= <Qualifier> <IDs>
def Declaration():
    global current_token, switch, output_file
    if switch == False:
        print("\t<Declaration> ::= <Qualifier> <IDs>")
        with open(output_file, "a") as file:
            file.write("\t<Declaration> ::= <Qualifier> <IDs>\n")
    if current_token['lexeme'] == '{':
        get_next_token()
        print_token()
    Qualifier()
    IDs()


# Rule 16
# R16) <IDs> ::= <Identifier> <IDs Prime>
def IDs():
    global current_token, switch, output_file, DECLARATION_LIST
    if switch == False:
        print("\t<IDs> ::= <Identifier> <IDs Prime>")
        with open(output_file, "a") as file:
            file.write("\t<IDs> ::= <Identifier> <IDs Prime>\n")
    if current_token['token'] == 'identifier':
        if DECLARATION_LIST == True:
            insert_symbol_table(current_token)
        else:
            gen_instruction("POPM", get_address(current_token['lexeme']))
        get_next_token()
        print_token()
        IDsPrime()
    else:
        
        print(f"Error: Expected 'identifier' at line {current_token['line']}.")
        print(f"Reading token:", end="")
        with open(output_file, "a") as file:
            file.write(f"Error: Expected 'identifier' at line {current_token['line']}.\n")
            file.write(f"Reading token:")
        print_token()
        exit_syntax_analyzer()


# Rule 17
# R17) <IDs Prime> ::= , <IDs> | <Empty>
def IDsPrime():
    global current_token, switch, output_file
    if switch == False:
        print("\t<IDs Prime> ::= , <IDs> | <Empty>")
        with open(output_file, "a") as file:
            file.write("\t<IDs Prime> ::= , <IDs> | <Empty>\n")
    if current_token['lexeme'] == ',':
        get_next_token()
        print_token()
        IDs()
    else:
        Empty()


# Rule 18
# R18) <Statement List> ::= <Statement> <Statement List Prime>
def StatementList():
    global current_token, switch, output_file
    if switch == False:
        print("\t<Statement List> ::= <Statement> <Statement List Prime>")
        with open(output_file, "a") as file:
            file.write("\t<Statement List> ::= <Statement> <Statement List Prime>\n")
    Statement()
    if current_token['lexeme'] != '#':
        StatementListPrime()
    


# Rule 19
# R19) <Statement List Prime> ::= <Statement List> | <Empty>
def StatementListPrime():
    global current_token, switch, output_file
    if switch == False:
        print("\t<Statement List Prime> ::= <Statement List> | <Empty>")
        with open(output_file, "a") as file:
            file.write("\t<Statement List Prime> ::= <Statement List> | <Empty>\n")
    if current_token['lexeme'] != '}':
        StatementList()
    else:
        Empty()


# Rule 20
# R20) <Statement> ::= <Compound> | <Assign> | <If> | <Return> | <Print> | <Scan> | <While>
def Statement():
    global current_token, switch, output_file
    if switch == False:
        print("\t<Statement> ::= <Compound> | <Assign> | <If> | <Return> | <Print> | <Scan> | <While>")
        with open(output_file, "a") as file:
            file.write("\t<Statement> ::= <Compound> | <Assign> | <If> | <Return> | <Print> | <Scan> | <While>\n")
    if current_token['lexeme'] == 'if':
        If()
    elif current_token['lexeme'] == 'while':
        While()
    elif current_token['lexeme'] == 'put':
        Print_put()
    elif current_token['lexeme'] == 'get':
        Scan()
    elif current_token['lexeme'] == 'ret':
        Return()
    elif current_token['token'] == 'identifier':
        Assign()
    elif current_token['lexeme'] == '{':
        Compound()
    else:
        
        print(f"Error: Expected 'if', 'while', 'put', 'get', 'ret', 'identifier' or '{{' at line {current_token['line']}.")
        print(f"Reading token:", end="")
        with open(output_file, "a") as file:
            file.write(f"Error: Expected 'if', 'while', 'put', 'get', 'ret', 'identifier' or '{{' at line {current_token['line']}.\n")
            file.write(f"Reading token:")
        print_token()
        exit_syntax_analyzer()


# Rule 21
# R21) <Compound> ::= { <Statement List> }
def Compound():
    global current_token, switch, output_file
    if switch == False:
        print("\t<Compound> ::= { <Statement List> }")
        with open(output_file, "a") as file:
            file.write("\t<Compound> ::= { <Statement List> }\n")
    if current_token['lexeme'] == '{':
        get_next_token()
        print_token()
        StatementList()
        if current_token['lexeme'] == '}':
            get_next_token()
            print_token()
        else:
            
            print(f"Error: Expected '}}' at line {current_token['line']}.")
            print(f"Reading token:", end="")
            with open(output_file, "a") as file:
                file.write(f"Error: Expected '}}' at line {current_token['line']}.\n")
                file.write(f"Reading token:")
                print_token()
            exit_syntax_analyzer()
    else:
        
        print(f"Error: Expected '{{' at line {current_token['line']}.")
        print(f"Reading token:", end="")
        with open(output_file, "a") as file:
            file.write(f"Error: Expected '{{' at line {current_token['line']}.\n")
            file.write(f"Reading token:")
        print_token()
        exit_syntax_analyzer()


# Rule 22
# R22) <Assign> ::= <Identifier> = <Expression> ;
def Assign():
    global current_token, switch, output_file
    if switch == False:
        print("\t<Assign> ::= <Identifier> = <Expression> ;")
        with open(output_file, "a") as file:
            file.write("\t<Assign> ::= <Identifier> = <Expression> ;\n")
    if current_token['token'] == 'identifier':
        save = current_token['lexeme']
        get_next_token()
        print_token()
        if current_token['lexeme'] == '=':
            get_next_token()
            print_token()
            Expression()
            gen_instruction("POPM", get_address(save))
            if current_token['lexeme'] == ';':
                get_next_token()
                print_token()
            else:
                
                print(f"Error: Expected ';' at line {current_token['line']}.")
                print(f"Reading token:", end="")
                with open(output_file, "a") as file:
                    file.write(f"Error: Expected ';' at line {current_token['line']}.\n")
                    file.write(f"Reading token:")
                    print_token()
                exit_syntax_analyzer()
        else:
            
            print(f"Error: Expected '=' at line {current_token['line']}.")
            print(f"Reading token:", end="")
            with open(output_file, "a") as file:
                file.write(f"Error: Expected '=' at line {current_token['line']}.\n")
                file.write(f"Reading token:")
                print_token()
            exit_syntax_analyzer()
    else:
        
        print(f"Error: Expected 'identifier' at line {current_token['line']}.")
        print(f"Reading token:", end="")
        with open(output_file, "a") as file:
            file.write(f"Error: Expected 'identifier' at line {current_token['line']}.\n")
            file.write(f"Reading token:")
        print_token()
        exit_syntax_analyzer()


# Rule 23
# R23) <If> ::= if ( <Condition> ) <Statement> <If Prime>
def If():
    global current_token, switch, output_file
    if switch == False:
        print("\t<If> ::= if ( <Condition> ) <Statement> <If Prime>")
        with open(output_file, "a") as file:
            file.write("\t<If> ::= if ( <Condition> ) <Statement> <If Prime>\n")
    if current_token['lexeme'] == 'if':
        get_next_token()
        print_token()
        if current_token['lexeme'] == '(':
            get_next_token()
            print_token()
            Condition()
            if current_token['lexeme'] == ')':
                get_next_token()
                print_token()
                Statement()
                back_patch(INSTRUCTION_ADDRESS)
                IfPrime()
            else:
                
                print(f"Error: Expected ')' at line {current_token['line']}.")
                print(f"Reading token:", end="")
                with open(output_file, "a") as file:
                    file.write(f"Error: Expected ')' at line {current_token['line']}.\n")
                    file.write(f"Reading token:")
                    print_token()
                exit_syntax_analyzer()
        else:
            
            print(f"Error: Expected '(' at line {current_token['line']}.")
            print(f"Reading token:", end="")
            with open(output_file, "a") as file:
                file.write(f"Error: Expected '(' at line {current_token['line']}.\n")
                file.write(f"Reading token:")
                print_token()
            exit_syntax_analyzer()
    else:
        
        print(f"Error: Expected 'if' keyword at line {current_token['line']}.")
        print(f"Reading token:", end="")
        with open(output_file, "a") as file:
            file.write(f"Error: Expected 'if' keyword at line {current_token['line']}.\n")
            file.write(f"Reading token:")
        print_token()
        exit_syntax_analyzer()

# Rule 24
# R24) <If Prime> ::= endif | else <Statement> endif
def IfPrime():
    global current_token, switch, output_file
    if switch == False:
        print("\t<If Prime> ::= endif | else <Statement> endif")
        with open(output_file, "a") as file:
            file.write("\t<If Prime> ::= endif | else <Statement> endif\n")
    if current_token['lexeme'] == 'endif':
        # TODO: might need to remove label from here 
        gen_instruction("LABEL", None)
        get_next_token()
        print_token()
    elif current_token['lexeme'] == 'else':
        gen_instruction("LABEL", None)
        get_next_token()
        print_token()
        Statement()
        if current_token['lexeme'] == 'endif':
            gen_instruction("LABEL", None)
            get_next_token()
            print_token()
        else:
            
            print(f"Error: Expected 'endif' keyword at line {current_token['line']}.")
            print(f"Reading token:", end="")
            with open(output_file, "a") as file:
                file.write(f"Error: Expected 'endif' keyword at line {current_token['line']}.\n")
                file.write(f"Reading token:")
                print_token()
            exit_syntax_analyzer()
    else:
        
        print(f"Error: Expected 'endif' or 'else' keyword at line {current_token['line']}.")
        print(f"Reading token:", end="")
        with open(output_file, "a") as file:
            file.write(f"Error: Expected 'endif' or 'else' keyword at line {current_token['line']}.\n")
            file.write(f"Reading token:")
        print_token()
        exit_syntax_analyzer()

# Rule 25
# R25) <Return> ::= ret <Return Prime>
def Return():
    global current_token, switch, output_file
    if switch == False:
        print("\t<Return> ::= return <Return Prime>")
        with open(output_file, "a") as file:
            file.write("\t<Return> ::= return <Return Prime>\n")
    if current_token['lexeme'] == 'ret':
        get_next_token()
        print_token()
        ReturnPrime()
    else:
        
        print(f"Error: Expected 'ret' keyword at line {current_token['line']}.")
        print(f"Reading token:", end="")
        with open(output_file, "a") as file:
            file.write(f"Error: Expected 'ret' keyword at line {current_token['line']}.\n")
            file.write(f"Reading token:")
        print_token()
        exit_syntax_analyzer()

# Rule 26
# R26) <Return Prime> ::= ; | <Expression> ;
def ReturnPrime():
    global current_token, switch, output_file
    if switch == False:
        print("\t<Return Prime> ::= ; | <Expression> ;")
        with open(output_file, "a") as file:
            file.write("\t<Return Prime> ::= ; | <Expression> ;\n")
    if current_token['lexeme'] == ';':
        get_next_token()
        print_token()
    else:
        Expression()
        if current_token['lexeme'] == ';':
            get_next_token()
            print_token()
        else:
            
            print(f"Error: Expected ';' at line {current_token['line']}.")
            print(f"Reading token:", end="")
            with open(output_file, "a") as file:
                file.write(f"Error: Expected ';' at line {current_token['line']}.\n")
                file.write(f"Reading token:")
                print_token()
            exit_syntax_analyzer()

# Rule 27
# R27) <Print> ::= put ( <Expression> );
def Print_put():
    global current_token, switch, output_file
    if switch == False:
        print("\t<Print> ::= put ( <Expression> );")
        with open(output_file, "a") as file:
            file.write("\t<Print> ::= put ( <Expression> );\n")
    if current_token['lexeme'] == 'put':
        get_next_token()
        print_token()
        if current_token['lexeme'] == '(':
            get_next_token()
            print_token()
            Expression()
            if current_token['lexeme'] == ')':
                get_next_token()
                print_token()
                if current_token['lexeme'] == ';':
                    get_next_token()
                    print_token()
                    gen_instruction("STDOUT", None)
                else:
                    
                    print(f"Error: Expected ';' at line {current_token['line']}.")
                    print(f"Reading token:", end="")
                    with open(output_file, "a") as file:
                        file.write(f"Error: Expected ';' at line {current_token['line']}.\n")
                        file.write(f"Reading token:")
                        print_token()
                    exit_syntax_analyzer()
            else:
                
                print(f"Error: Expected ')' at line {current_token['line']}.")
                print(f"Reading token:", end="")
                with open(output_file, "a") as file:
                    file.write(f"Error: Expected ')' at line {current_token['line']}.\n")
                    file.write(f"Reading token:")
                    print_token()
                exit_syntax_analyzer()
        else:
            
            print(f"Error: Expected '(' at line {current_token['line']}.")
            print(f"Reading token:", end="")
            with open(output_file, "a") as file:
                file.write(f"Error: Expected '(' at line {current_token['line']}.\n")
                file.write(f"Reading token:")
                print_token()
            exit_syntax_analyzer()
    else:
        
        print(f"Error: Expected 'put' keyword at line {current_token['line']}.")
        print(f"Reading token:", end="")
        with open(output_file, "a") as file:
            file.write(f"Error: Expected 'put' keyword at line {current_token['line']}.\n")
            file.write(f"Reading token:")
        print_token()
        exit_syntax_analyzer()

# Rule 28
# R28) <Scan> ::= get ( <IDs> );
def Scan():
    global current_token, switch, output_file
    if switch == False:
        print("\t<Scan> ::= get ( <IDs> );")
        with open(output_file, "a") as file:
            file.write("\t<Scan> ::= get ( <IDs> );\n")
    if current_token['lexeme'] == 'get':
        gen_instruction("STDIN", None)
        get_next_token()
        print_token()
        if current_token['lexeme'] == '(':
            get_next_token()
            print_token()
            IDs()
            if current_token['lexeme'] == ')':
                get_next_token()
                print_token()
                if current_token['lexeme'] == ';':
                    get_next_token()
                    print_token()
                else:
                    
                    print(f"Error: Expected ';' at line {current_token['line']}.")
                    print(f"Reading token:", end="")
                    with open(output_file, "a") as file:
                        file.write(f"Error: Expected ';' at line {current_token['line']}.\n")
                        file.write(f"Reading token:")
                        print_token()
                    exit_syntax_analyzer()
            else:
                
                print(f"Error: Expected ')' at line {current_token['line']}.")
                print(f"Reading token:", end="")
                with open(output_file, "a") as file:
                    file.write(f"Error: Expected ')' at line {current_token['line']}.\n")
                    file.write(f"Reading token:")
                    print_token()
                exit_syntax_analyzer()
        else:
            
            print(f"Error: Expected '(' at line {current_token['line']}.")
            print(f"Reading token:", end="")
            with open(output_file, "a") as file:
                file.write(f"Error: Expected '(' at line {current_token['line']}.\n")
                file.write(f"Reading token:")
                print_token()
            exit_syntax_analyzer()
    else:
        
        print(f"Error: Expected 'get' keyword at line {current_token['line']}.")
        print(f"Reading token:", end="")
        with open(output_file, "a") as file:
            file.write(f"Error: Expected 'get' keyword at line {current_token['line']}.\n")
            file.write(f"Reading token:")
        print_token()
        exit_syntax_analyzer()

# Rule 29
# R29) <While> ::= while ( <Condition> ) <Statement>
def While():
    global current_token, switch, output_file
    if switch == False:
        print("\t<While> ::= while ( <Condition> ) <Statement>")
        with open(output_file, "a") as file:
            file.write("\t<While> ::= while ( <Condition> ) <Statement>\n")
    if current_token['lexeme'] == 'while':
        address = INSTRUCTION_ADDRESS
        gen_instruction("LABEL", None)
        get_next_token()
        print_token()
        if current_token['lexeme'] == '(':
            get_next_token()
            print_token()
            Condition()
            if current_token['lexeme'] == ')':
                get_next_token()
                print_token()
                Statement()
                gen_instruction("JUMP", address)
                back_patch(INSTRUCTION_ADDRESS)
            else:
                
                print(f"Error: Expected ')' at line {current_token['line']}.")
                print(f"Reading token:", end="")
                with open(output_file, "a") as file:
                    file.write(f"Error: Expected ')' at line {current_token['line']}.\n")
                    file.write(f"Reading token:")
                    print_token()
                exit_syntax_analyzer
        else:
            
            print(f"Error: Expected '(' at line {current_token['line']}.")
            print(f"Reading token:", end="")
            with open(output_file, "a") as file:
                file.write(f"Error: Expected '(' at line {current_token['line']}.\n")
                file.write(f"Reading token:")
                print_token()
            exit_syntax_analyzer()
    else:
        
        print(f"Error: Expected 'while' keyword at line {current_token['line']}.")
        print(f"Reading token:", end="")
        with open(output_file, "a") as file:
            file.write(f"Error: Expected 'while' keyword at line {current_token['line']}.\n")
            file.write(f"Reading token:")
        print_token()
        exit_syntax_analyzer()


# Rule 30
# R30) <Condition> ::= <Expression> <Relop> <Expression>
def Condition():
    global current_token, switch, output_file, INSTRUCTION_ADDRESS
    if switch == False:
        print("\t<Condition> ::= <Expression> <Relop> <Expression>")
        with open(output_file, "a") as file:
            file.write("\t<Condition> ::= <Expression> <Relop> <Expression>\n")
    Expression()
    operand = current_token['lexeme']
    Relop()
    Expression()
    # handle instructions here 
    if operand == '==':
        gen_instruction("EQU", None)
        push_jumpstack(INSTRUCTION_ADDRESS)
        gen_instruction("JUMPZ", None)
    elif operand == '!=':
        gen_instruction("NEQ", None)
        push_jumpstack(INSTRUCTION_ADDRESS)
        gen_instruction("JUMPZ", None)
    elif operand == '>':
        gen_instruction("GRT", None)
        push_jumpstack(INSTRUCTION_ADDRESS)
        gen_instruction("JUMPZ", None)
    elif operand == '<':
        gen_instruction("LES", None)
        push_jumpstack(INSTRUCTION_ADDRESS)
        gen_instruction("JUMPZ", None)
    elif operand == '<=':
        gen_instruction("LEQ", None)
        push_jumpstack(INSTRUCTION_ADDRESS)
        gen_instruction("JUMPZ", None)
    elif operand == '=>':
        gen_instruction("GEQ", None)
        push_jumpstack(INSTRUCTION_ADDRESS)
        gen_instruction("JUMPZ", None)


# Rule 31
# R31) <Relop> ::= == | != | > | < | <= | =>
def Relop():
    global current_token, switch, output_file
    if switch == False:
        print("\t<Relop> ::= == | != | > | < | <= | =>")
        with open(output_file, "a") as file:
            file.write("\t<Relop> ::= == | != | > | < | <= | =>\n")
    if current_token['lexeme'] in ['==', '!=', '>', '<', '<=', '=>']:
        get_next_token()
        print_token()
    
    else:
        
        print(f"Error: Expected '==', '!=', '>', '<', '<=' or '=>' at line {current_token['line']}.")
        print(f"Reading token:", end="")
        with open(output_file, "a") as file:
            file.write(f"Error: Expected '==', '!=', '>', '<', '<=' or '=>' at line {current_token['line']}.\n")
            file.write(f"Reading token:")
        print_token()
        exit_syntax_analyzer()


# Rule 32
# R32) <Expression> ::= <Term> <Expression Prime>
def Expression():
    global current_token, switch, output_file
    if switch == False:
        print("\t<Expression> ::= <Term> <Expression Prime>")
        with open(output_file, "a") as file:
            file.write("\t<Expression> ::= <Term> <Expression Prime>\n")
    Term()
    ExpressionPrime()


# Rule 33
# R33) <Expression Prime> ::= + <Term> <Expression Prime> | - <Term> <Expression Prime> | <Empty>
def ExpressionPrime():
    global current_token, switch, output_file
    if switch == False:
        print("\t<Expression Prime> ::= + <Term> <Expression Prime> | - <Term> <Expression Prime> | <Empty>")
        with open(output_file, "a") as file:
            file.write("\t<Expression Prime> ::= + <Term> <Expression Prime> | - <Term> <Expression Prime> | <Empty>\n")
    if current_token['lexeme'] == '+':
        get_next_token()
        print_token()
        Term()
        gen_instruction("ADD", None)
        ExpressionPrime()
    elif current_token['lexeme'] == '-':
        get_next_token()
        print_token()
        Term()
        gen_instruction("SUB", None)
        ExpressionPrime()
    else:
        Empty()


# Rule 34
# R34) <Term> ::= <Factor> <Term Prime>
def Term():
    global current_token, switch, output_file
    if switch == False:
        print("\t<Term> ::= <Factor> <Term Prime>")
        with open(output_file, "a") as file:
            file.write("\t<Term> ::= <Factor> <Term Prime>\n")
    Factor()
    TermPrime()


# Rule 35
# R35) <Term Prime> ::= * <Factor> <Term Prime> | / <Factor> <Term Prime> | <Empty>
def TermPrime():
    global current_token, switch, output_file
    if switch == False:
        print("\t<Term Prime> ::= * <Factor> <Term Prime> | / <Factor> <Term Prime> | <Empty>")
        with open(output_file, "a") as file:
            file.write("\t<Term Prime> ::= * <Factor> <Term Prime> | / <Factor> <Term Prime> | <Empty>\n")
    if current_token['lexeme'] == '*':
        get_next_token()
        print_token()
        Factor()
        gen_instruction("MUL", None)
        TermPrime()
    elif current_token['lexeme'] == '/':
        get_next_token()
        print_token()
        Factor()
        gen_instruction("DIV", None)
        TermPrime()
    else:
        Empty()


# Rule 36 
# R36) <Factor> ::= - <Primary> | <Primary>
def Factor():
    global current_token, switch, output_file
    if switch == False:
        print("\t<Factor> ::= - <Primary> | <Primary>")
        with open(output_file, "a") as file:
            file.write("\t<Factor> ::= - <Primary> | <Primary>\n")
    if current_token['lexeme'] == '-':
        get_next_token()
        print_token()
        Primary()
    else:
        Primary()


# Rule 37
# R37) <Primary> ::= <Identifier> <Primary Prime> | <Integer> | ( <Expression> ) | true | false
def Primary():
    global current_token, switch, output_file
    if switch == False:
        print("\t<Primary> ::= <Identifier> <Primary Prime> | <Integer> | ( <Expression> ) | true | false")
        with open(output_file, "a") as file:
            file.write("\t<Primary> ::= <Identifier> <Primary Prime> | <Integer> | ( <Expression> ) | true | false\n")
    if current_token['token'] == 'identifier':
        address = get_address(current_token['lexeme'])
        # TODO: ADD ERROR HERE 
        if address == None:
            print(f"Error: Identifier '{current_token['lexeme']}' not declared at line {current_token['line']}.")
            print("Identifier should be declared prior to use.")
            with open(output_file, "a") as file:
                file.write(f"Error: Identifier '{current_token['lexeme']}' not declared at line {current_token['line']}.\n")
                file.write("Identifier should be declared prior to use.\n")
            exit_syntax_analyzer()
        else:
            gen_instruction("PUSHM", address)
        get_next_token()
        print_token()
        PrimaryPrime()
    elif current_token['token'] == 'integer':
        gen_instruction("PUSHI", current_token['lexeme'])
        get_next_token()
        print_token()
    elif current_token['lexeme'] == '(':
        get_next_token()
        print_token()
        Expression()
        if current_token['lexeme'] == ')':
            get_next_token()
            print_token()
        else:
            
            print(f"Error: Expected ')' at line {current_token['line']}.")
            print(f"Reading token:", end="")
            with open(output_file, "a") as file:
                file.write(f"Error: Expected ')' at line {current_token['line']}.\n")
                file.write(f"Reading token:")
                print_token()
            exit_syntax_analyzer()
    # removing real from here
    # elif current_token['token'] == 'real':
    #     get_next_token()
    #     print_token()
    elif current_token['lexeme'] == 'true':
        gen_instruction("PUSHI", 1)
        get_next_token()
        print_token()
    elif current_token['lexeme'] == 'false':
        gen_instruction("PUSHI", 0)
        get_next_token()
        print_token()
    else:
        
        print(f"Error: Expected 'identifier', 'integer', '(', 'true' or 'false' at line {current_token['line']}.")
        print(f"Reading token:", end="")
        with open(output_file, "a") as file:
            file.write(f"Error: Expected 'identifier', 'integer', '(', 'true' or 'false' at line {current_token['line']}.\n")
            file.write(f"Reading token:")
        print_token()
        exit_syntax_analyzer()

# Rule 38
# R38) <Primary Prime> ::= <Empty> | ( <IDs> )
def PrimaryPrime():
    global current_token, switch, output_file
    if switch == False:
        print("\t<Primary Prime> ::= <Empty> | ( <IDs> )")
        with open(output_file, "a") as file:
            file.write("\t<Primary Prime> ::= <Empty> | ( <IDs> )\n")
    if current_token['lexeme'] == '(':
        get_next_token()
        print_token()
        IDs()
        if current_token['lexeme'] == ')':
            get_next_token()
            print_token()
        else:
            
            print(f"Error: Expected ')' at line {current_token['line']}.")
            print(f"Reading token:", end="")
            with open(output_file, "a") as file:
                file.write(f"Error: Expected ')' at line {current_token['line']}.\n")
                file.write(f"Reading token:")
                print_token()
            exit_syntax_analyzer()
    else:
        Empty()


# Rule 39
# R39) <Empty> ::= <Empty>
def Empty():
    global current_token, switch, output_file
    if switch == False:
        print("\t<Empty> ::= <Empty>")
        with open(output_file, "a") as file:
            file.write("\t<Empty> ::= <Empty>\n")
    pass    
    

# *********************************************************************************************************************************
# ******************************SYNTAX ANALYZER CODE ENDS HERE********************************************************************* 
# *********************************************************************************************************************************



# Code to read the file and store its words in an array
def read_file(file_name):
    try:
        with open(file_name, 'r') as file:
            # here we store the current word read
            word = ""
            while True:
                char = file.read(1)
                if not char:
                    break  # End of file, we exit loop
                # check for new line character
                if char == '\n':
                    if word:
                        words.append(word)
                        word = ""
                    words.append(char)
                # check for comments
                elif char == '[':
                    if word:
                        words.append(word)
                        word = ""
                    # check for correct opening comment
                    next_char = file.read(1)
                    if char + next_char == begin_comment:
                        words.append(char + next_char)
                    else:
                        # store single operator 
                        words.append(char)
                        # check if next character is a separator
                        if next_char in separator:
                            if next_char != ' ' and char != '\n' and char != '\t':
                                words.append(next_char)
                        else:    
                            word += next_char

                elif char in operators: # read operator
                    if word:
                        words.append(word)
                        word = ""
                    # check for double character operators
                    next_char = file.read(1)
                    # check for closing comment
                    if char + next_char == end_comment:
                        words.append(char + next_char)

                    elif char + next_char in operators:
                        words.append(char + next_char)
                    else:
                        # store single operator 
                        words.append(char)
                        # check if next character is a separator
                        if next_char in separator:
                            if next_char != ' ' and char != '\n' and char != '\t':
                                words.append(next_char)
                        # remove next if in case that we want to make this illegal
                        elif next_char in operators:
                            words.append(next_char)
                        else:    
                            word = next_char

                elif char in separator: # read separator
                    if word:
                        words.append(word)
                        word = ""
                    # in case that we dont want to store whitespaces
                    #remove "if" to keep whitespaces
                    if char != ' ' and char != '\t':
                        words.append(char)
                else:
                    word += char
            if word:
                words.append(word)
    except FileNotFoundError:
        print(f"The file '{file_name}' was not found.")
    except PermissionError:
        print(f"You do not have permission to read the file: '{file_name}'.")
    except OSError as systemError:  
        print(f"An error occurred while reading the file: '{file_name}'. The error was: {systemError}")
    except Exception as errorMessage:
        print(f"An unexpected error occurred while reading the file: '{file_name}'. The error was: {str(errorMessage)}")

# finite state machine for real and integer
def FSMReal(lexeme):
    current_state = 1
    for char in lexeme:
        # manage initial state
        # we need this because we can't have a "." as the first character
        if current_state == 1:
            if char.isdigit():
                current_state = 2
            else:
                current_state = 5
        # manage state 2 aka integer before "."
        if current_state == 2:
            if char.isdigit():
                current_state = 2
            elif char == '.':
                current_state = 3
            else:
                current_state = 5
        # manage state 3 aka "."
        elif current_state == 3:
            if char.isdigit():
                current_state = 4
            else:
                current_state = 5
        # manage state 4 aka integer after "."
        elif current_state == 4:
            if char.isdigit():
                current_state = 4
            else:
                current_state = 5

    # if our final state is 4, then we have a real
    if current_state == 4:
        # store token and lexeme
        tokens.append({'token': 'real', 'lexeme': lexeme, 'line': current_line})
    # if our final state is 2, then we have an integer
    elif current_state == 2:
        tokens.append({'token': 'integer', 'lexeme': lexeme, 'line': current_line})
    # in case of failure
    else:
        tokens.append({'token': 'illegal', 'lexeme': lexeme, 'line': current_line})

# finite state machine for identifiers
def FSMIdentifier(identifier):
    current_state = 1
    if len(identifier) == 1:
        if identifier.isalpha():
            tokens.append({'token': 'identifier', 'lexeme': identifier, 'line': current_line})
    else:
        for char in identifier:
            # check if the first character is a letter
            if current_state == 1:
                if char.isalpha():
                    current_state = 2
                else:
                    current_state = 4
            # now we can accept digits and letters
            elif current_state == 2:
                if char.isalpha():
                    # we stay in the same state if letter
                    current_state = 2
                elif char.isdigit():
                    # we move to state 3 if digit
                    current_state = 3
                else:
                    current_state = 4
            # still accepting digits and letters
            elif current_state == 3:
                if char.isalpha():
                    # we go back to state 2 if letter
                    current_state = 2
                elif char.isdigit():
                    # we stay in the same state if digit
                    current_state = 3
                else:
                    current_state = 4
        # final state must be 2 because we need to end in a letter
        if current_state == 2:
            tokens.append({'token': 'identifier', 'lexeme': identifier, 'line': current_line})
        else:
            tokens.append({'token': 'illegal', 'lexeme': identifier, 'line': current_line})

# this is the main lexer function, it is in charge of identifying the tokens
def lexer(word):
    if word in keyword:
        tokens.append({'token': 'keyword', 'lexeme': word, 'line': current_line})
    elif word in operators:
        # check that word is not the only illegal operator "!", only in list for "!="
        if word == '!':
            tokens.append({'token': 'illegal', 'lexeme': word, 'line': current_line})
        else:
            tokens.append({'token': 'operator', 'lexeme': word, 'line': current_line})
    elif word in separator:
        tokens.append({'token': 'separator', 'lexeme': word, 'line': current_line})
    # check if it is a real or an integer
    elif word[0].isdigit():
        FSMReal(word)
    # check if is in an identifier
    elif word[0].isalpha():
        FSMIdentifier(word)
    else:
        tokens.append({'token': 'illegal', 'lexeme': word, 'line': current_line})

# this functions removes comments from the code
def commentRemoval(words):
    global current_line
    # keep track if we are in a comment 
    comment = False
    # iterate through lexemes 
    for word in words:
        if word == "\n":
            current_line += 1
        elif word == begin_comment:
            comment = True
        elif comment == False:
            lexer(word)
        elif word == end_comment:
            comment = False

# this functions prints all the tokens to the main program console
def print_tokens(tokens):
    print("token\t\t\tlexeme\t\t\tline")
    print("_________________________________\n")
    for token in tokens:
        if token['token'] == 'illegal' or token['token'] == 'keyword' or token['token'] == 'integer' or token['token'] == 'real':
            print(f"{token['token']}\t\t\t{token['lexeme']}\t\t\t{token['line']}")
        else:
            print(f"{token['token']}\t\t{token['lexeme']}\t\t\t{token['line']}")

# this function generates a file name for the tokens file
def file_name_generator(file_name):
    return 'output_' + file_name

# this function writes all the tokens and lexemes to a file
def write_tokens(tokens):
    global output_file
    try:
        with open(output_file, 'w') as file:
            print(f"\nWriting tokens to file '{output_file}'...\n")
            file.write("token\t\t\tlexeme\t\t\tline\n")
            file.write("_________________________________\n")
            for token in tokens:
                if token['token'] == 'illegal' or token['token'] == 'keyword' or token['token'] == 'integer' or token['token'] == 'real':
                    file.write(f"{token['token']}\t\t\t{token['lexeme']}\t\t\t{token['line']}\n")
                else:
                    file.write(f"{token['token']}\t\t{token['lexeme']}\t\t\t{token['line']}\n")
            print(f"Tokens written to file '{output_file}' successfully!\n")
    except FileNotFoundError:
        print(f"The file '{output_file}' was not found.")
    except PermissionError:
        print(f"You do not have permission to create the file: '{output_file}'.")
    except OSError as systemError:  
        print(f"An error occurred while creating the file: '{output_file}'. The error was: {systemError}")
    except Exception as errorMessage:
        print(f"An unexpected error occurred while creating the file: '{output_file}'. The error was: {str(errorMessage)}")

# Function to analyze a file
def analyze_file():
    global current_line, output_file, switch, token_index, LAST_IDENTIFIER_TYPE, MEMORY_ADDRESS, INSTRUCTION_ADDRESS, DECLARATION_LIST
    while True:
        try:
            file_name = input("Please enter the name of the file you want to analyze (or 'q' to quit): ").strip().lower()
            if file_name == 'q':
                print("\nThank you for using our Assignment 3!\n")
                print("Exiting program...")
                time.sleep(2)
                sys.exit(0) # Exit the loop and quit the program
            with open(file_name, 'r') as file:
                # The file exists, so continue with analysis
                # create output file name
                output_file = file_name_generator(file_name)
                # clear file in case that there was a previous analysis
                with open(output_file, "w") as file:
                    file.write("")  # This will clear the file's contents
                # ask user if they want syntax rules printed
                while True:
                    print_rules = input("Do you want to print the syntax rules? (yes/no): ").strip().lower()
                    if print_rules == 'yes' or print_rules == 'y':
                        switch = False
                        break
                    elif print_rules == 'no' or print_rules == 'n':
                        switch = True
                        break
                    else:
                        print("Invalid input. Please enter 'yes' or 'no'.")
                print(f"\nAnalyzing file '{file_name}'...\n")
                # switch = False  # Set switch to False to print the rules
                words.clear()  # Clear the list of words from previous analyses
                tokens.clear()  # Clear the list of tokens from previous analyses
                symbol_table.clear()  # Clear the symbol table from previous analyses
                assembly_code.clear()  # Clear the assembly code from previous analyses
                current_line = 1  # Reset the current line to 1
                token_index = 0  # Reset the token index to 0
                DECLARATION_LIST = True  # Set the declaration list to True
                LAST_IDENTIFIER_TYPE = None # Reset the last identifier type to None
                MEMORY_ADDRESS = 7000 # Reset the memory address to 7000
                INSTRUCTION_ADDRESS = 1 # Reset the instruction address to 1
                read_file(file_name)
                commentRemoval(words)
                Rat23F()        # Run the syntax analyzer
                print_symbol_table()
                print_assembly_code()
                break
        except FileNotFoundError:
            print(f"The file '{file_name}' was not found. Please enter a valid file name.")
        except PermissionError:
            print(f"You do not have permission to read the file: '{file_name}'. Please enter a different file name.")
        except Exception as errorMessage:
            print(f"An unexpected error occurred: {str(errorMessage)} Please enter a different file name.")

def main():
    # User interface
    print("\nWelcome to our Assignment 3!")

    # call main function to analyze a file 
    analyze_file()
    # Main loop
    while True:
        another_analysis = input("Do you want to analyze another file? (yes/no): ").strip().lower()
        if another_analysis == 'no' or another_analysis == 'n':
            print("\nThank you for using our Assignment 3!\n")
            print("Exiting program...")
            time.sleep(2)
            sys.exit(0)  # Exit the program if the user does not want to analyze another file
        elif another_analysis == 'yes' or another_analysis == 'y':
            analyze_file()
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")



if __name__ == "__main__":
    main()
