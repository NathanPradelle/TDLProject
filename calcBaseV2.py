# -*- coding: utf-8 -*-

from genereTreeGraphviz2 import printTreeGraph

reserved = {
    'print': 'PRINT',
    'if': 'IF',
    'while': 'WHILE',
    'else': 'ELSE',
    'for': 'FOR',
    'return': 'RETURN',
    'global': 'GLOBAL'
}

tokens = ['NUMBER', 'MINUS', 'PLUS', 'TIMES', 'DIVIDE', 'LPAREN',
          'RPAREN', 'OR', 'AND', 'SEMI', 'EGAL', 'NAME', 'INF', 'SUP',
          'EGALEGAL', 'INFEG', 'LBRACE', 'RBRACE', 'COMMA', 'COMMENT'] + list(reserved.values())

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_OR = r'\|'
t_AND = r'\&'
t_SEMI = r';'
t_EGAL = r'='
t_INF = r'\<'
t_SUP = r'>'
t_INFEG = r'\<='
t_EGALEGAL = r'=='
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','
t_COMMENT = r'\#.*'

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'NAME')
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

import ply.lex as lex
lex.lex()

names = {}
functions = {}
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'INF', 'INFEG', 'EGALEGAL', 'SUP'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)

def evalExpr(t, local_vars=None):

    if isinstance(t, int):
        return t
    elif isinstance(t, str):
        if local_vars is not None and t in local_vars:
            if isinstance(local_vars, dict) and t in names:
                return names[t]
            else:
                return local_vars[t]
        elif t in names:
            return names[t]
        else:
            raise NameError(f"DEBUG ERROR: Variable '{t}' non définie.")


    if isinstance(t, tuple):
        if t[0] == '+':
            return evalExpr(t[1], local_vars) + evalExpr(t[2], local_vars)
        elif t[0] == '-':
            return evalExpr(t[1], local_vars) - evalExpr(t[2], local_vars)
        elif t[0] == '*':
            return evalExpr(t[1], local_vars) * evalExpr(t[2], local_vars)
        elif t[0] == '/':
            return evalExpr(t[1], local_vars) // evalExpr(t[2], local_vars)
        elif t[0] == '<':
            return evalExpr(t[1], local_vars) < evalExpr(t[2], local_vars)
        elif t[0] == '>':
            return evalExpr(t[1], local_vars) > evalExpr(t[2], local_vars)
        elif t[0] == '==':
            return evalExpr(t[1], local_vars) == evalExpr(t[2], local_vars)
        elif t[0] == '<=':
            return evalExpr(t[1], local_vars) <= evalExpr(t[2], local_vars)
        elif t[0] == '>=':
            return evalExpr(t[1], local_vars) >= evalExpr(t[2], local_vars)
        elif t[0] == 'and':
            return evalExpr(t[1], local_vars) and evalExpr(t[2], local_vars)
        elif t[0] == 'or':
            return evalExpr(t[1], local_vars) or evalExpr(t[2], local_vars)

        raise ValueError(f"DEBUG ERROR: Expression inconnue : {t}")





def evalInst(p, local_vars=None):
    try:
        global names
        if local_vars is None:
            local_vars = {}
        if isinstance(p, tuple):
            if p[0] == 'bloc':
                result = evalInst(p[1], local_vars)
                if result is not None:
                    return result
                if p[2] != 'empty':
                    result = evalInst(p[2], local_vars)
                    if result is not None:
                        return result
            elif p[0] == 'print':
                value = evalExpr(p[1], local_vars)
                print("calc >", value)
            elif p[0] == 'assign':
                names[p[1]] = evalExpr(p[2], local_vars)
            elif p[0] == 'if':
                if evalExpr(p[1], local_vars):
                    return evalInst(p[2], local_vars)
            elif p[0] == 'if_else':
                if evalExpr(p[1], local_vars):
                    return evalInst(p[2], local_vars)
                else:
                    return evalInst(p[3], local_vars)
            elif p[0] == 'for':
                evalInst(p[1], local_vars)
                while evalExpr(p[2], local_vars):
                    result = evalInst(p[4], local_vars)
                    if result is not None:
                        return result
                    evalInst(p[3], local_vars)
            elif p[0] == 'while':
                while evalExpr(p[1], local_vars):
                    result = evalInst(p[2], local_vars)
                    if result is not None:
                        return result
            elif p[0] == 'return':
                return evalExpr(p[1], local_vars)
            else:
                raise RuntimeError(f"Unknown instruction: {p}")
    except Exception as e:
        print(f"Execution error at line {p.lineno if hasattr(p, 'lineno') else 'unknown'}: {e}")


def p_start(p):
    'start : bloc'
    print(p[1])
    printTreeGraph(p[1])
    result = evalInst(p[1])
    if result is not None:
        print("calc >", result)


def p_bloc(p):
    '''bloc : bloc statement SEMI
    | statement SEMI'''
    if len(p) == 3:
        p[0] = ('bloc', p[1], 'empty')
    else:
        if p[1][0] == 'return':
            p[0] = p[1]
        else:
            p[0] = ('bloc', p[1], p[2])

def p_statement_expr(p):
    'statement : PRINT LPAREN expression RPAREN'
    p[0] = ('print', p[3])

def p_statement_assign(p):
    'statement : NAME EGAL expression'
    p[0] = ('assign', p[1], p[3])

def p_statement_if(p):
    'statement : IF LPAREN expression RPAREN LBRACE bloc RBRACE'
    p[0] = ('if', p[3], p[6])

def p_statement_if_else(p):
    'statement : IF LPAREN expression RPAREN LBRACE bloc RBRACE ELSE LBRACE bloc RBRACE'
    p[0] = ('if_else', p[3], p[6], p[10])

def p_statement_for(p):
    'statement : FOR LPAREN statement SEMI expression SEMI statement RPAREN LBRACE bloc RBRACE'
    p[0] = ('for', p[3], p[5], p[7], p[10])

def p_statement_while(p):
    'statement : WHILE LPAREN expression RPAREN LBRACE bloc RBRACE'
    p[0] = ('while', p[3], p[6])

def p_param_list(p):
    '''param_list :
        | NAME
        | param_list COMMA NAME'''
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_statement_return(p):
    'statement : RETURN expression'
    p[0] = ('return', p[2])

def p_statement_return_empty(p):
    'statement : RETURN'
    p[0] = ('return', None)

def p_expression_binop_inf(p):
    '''expression : expression INF expression
    | expression INFEG expression
    | expression EGALEGAL expression
    | expression AND expression
    | expression OR expression
    | expression PLUS expression
    | expression TIMES expression
    | expression MINUS expression
    | expression DIVIDE expression
    | expression SUP expression'''
    p[0] = (p[2], p[1], p[3])

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = p[1]

def p_expression_name(p):
    'expression : NAME'
    p[0] = p[1]

def p_statement_function_def(p):
    'statement : NAME LPAREN param_list RPAREN LBRACE bloc RBRACE'
    p[0] = ('function_def', p[1], p[3], p[6])



def p_statement_function_call(p):
    'statement : NAME LPAREN param_list RPAREN'
    p[0] = ('function_call', p[1], p[3])

def p_statement_global(p):
    'statement : GLOBAL NAME'
    p[0] = ('global', p[2])


def p_error(p):
    if p:
        print(f"Syntax error at token '{p.value}', line {p.lineno}, position {p.lexpos}")
    else:
        print("Syntax error: unexpected end of input")
    raise SyntaxError("Parsing error detected")

import ply.yacc as yacc
yacc.yacc()
s = '''
for (i = 0; i < 4; i = i + 1) { 
    print(i);
};
'''
yacc.parse(s)
