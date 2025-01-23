# -*- coding: utf-8 -*-

from genereTreeGraphviz2 import printTreeGraph

reserved = {
    'print': 'PRINT',
    'if':'IF',
    'while':'WHILE',
    'for':'FOR',
    'return':'RETURN',
}

tokens = ['NUMBER', 'MINUS', 'PLUS', 'TIMES', 'DIVIDE', 'LPAREN',
          'RPAREN', 'OR', 'AND', 'SEMI', 'EGAL', 'NAME', 'INF', 'SUP',
          'EGALEGAL', 'INFEG', 'LBRACE', 'RBRACE', 'COMMA'] + list(reserved.values())

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

global_scope ={}
local_scope =[{}]

def get_variable(name):
    for scope in reversed(local_scope):
        if name in scope:
            return scope[name]
    if name in global_scope:
        return global_scope[name]
    raise NameError(f"Variable '{name}' non trouvée")

def set_variable(name, value):
    for scope in reversed(local_scope):
        if name in scope:
            scope[name] = value
            return
    global_scope[name] = value

def enter_scope():
    local_scope.append({})

def exit_scope():
    if len(local_scope) > 1:
        local_scope.pop()
    else:
        raise Exception("Peut pas partir")

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
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'INF', 'INFEG', 'EGALEGAL', 'SUP'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)

def evalInst(p):
    if isinstance(p, tuple):
        def evalExpr(t):
            if isinstance(t, int): 
                return t
            if isinstance(t, str): 
                return get_variable(t)
            if t[0] == '+': 
                return eval(t[1]) + eval(t[2])
            if t[0] == '-': 
                return eval(t[1]) - eval(t[2])
            if t[0] == '*': 
                return eval(t[1]) * eval(t[2])
            if t[0] == '/': 
                return eval(t[1]) // eval(t[2])
            if t[0] == '<': 
                return eval(t[1]) < eval(t[2])
            if t[0] == '>': 
                return eval(t[1]) > eval(t[2])
        
        if p[0] == 'print':
            print(evalExpr(p[1]))
        elif p[0] == 'assign':
            set_variable(p[1], evalExpr(p[2]))
        elif p[0] == 'if':
            condition = evalExpr(p[1])
            if condition:
                evalInst(p[2])
        elif p[0] == 'while':
            while evalExpr(p[1]):
                evalInst(p[2])
        elif p[0] == 'for':
            evalInst(p[1])
            while evalExpr(p[2]):  
                evalInst(p[4])
                evalInst(p[3])  

def p_start(p):
    'start : bloc'
    print(p[1])
    printTreeGraph(p[1])
    evalInst(p[1])

def p_bloc(p):
    '''bloc : bloc statement SEMI
    | statement SEMI'''
    if len(p) == 3:
        p[0] = ('bloc', p[1], 'empty')
    else:
        p[0] = ('bloc', p[1], p[3])

def p_statement_expr(p):
    'statement : PRINT LPAREN expression RPAREN'
    p[0] = ('print', p[3])

def p_statement_assign(p):
    'statement : NAME EGAL expression'
    p[0] = ('assign', p[1], p[3])

def p_statement_if(p):
    'statement : IF LPAREN expression RPAREN statement'
    p[0] = ('if', p[3], p[5])

def p_statement_for(p):
    'statement : FOR LPAREN statement SEMI expression SEMI statement RPAREN statement'
    p[0] = ('for', p[3], p[5], p[7], p[9])

def p_statement_while(p):
    'statement : WHILE LPAREN expression RPAREN statement '
    p[0] = ('while', p[3], p[5])

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

def p_statement_fonction(p):
    'statement : NAME LPAREN param_list RPAREN LBRACE bloc RBRACE '
    enter_scope()  
    p[0] = (p[3], p[5])
    exit_scope()  

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

def p_error(p):    print("Syntax error in input!")

import ply.yacc as yacc
yacc.yacc()
s = 'print(1+2);'
yacc.parse(s)
