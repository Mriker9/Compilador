# coding: utf-8

from sly import Lexer
from collections import defaultdict
import os
import re
import sys


class CoolLexer(Lexer):
    tokens = {OBJECTID, INT_CONST, BOOL_CONST, TYPEID,
              ELSE, IF, FI, THEN, NOT, IN, CASE, ESAC, CLASS,
              INHERITS, ISVOID, LET, LOOP, NEW, OF,
              POOL, THEN, WHILE, NUMBER, STR_CONST, LE, DARROW, ASSIGN, ERROR, CMT_CONST1, CMT_CONST}

    literals = {'.', ',', '-', '+', '+', '=', ';', ':', '(', ')', '{', '}', '*', "'", '"', '>', '<', '~', '/', '@', '!', '?', '#', '$', '^', '_', '`', '%', '[', ']', '|', '\\'}

    # Keywords
    ELSE        = r'\b[eE][lL][sS][eE]\b'
    IF          = r'\b[iI][fF]\b'
    FI          = r'\b[fF][iI]\b'
    NOT         = r'\b[nN][oO][tT]\b'
    IN          = r'\b[iI][nN]\b'
    CASE        = r'\b[cC][aA][sS][eE]\b'
    ESAC        = r'\b[eE][sS][aA][cC]\b'
    CLASS       = r'\b[cC][lL][aA][sS][sS]\b'
    INHERITS    = r'\b[iI][nN][hH][eE][rR][iI][tT][sS]\b'
    ISVOID      = r'\b[iI][sS][vV][oO][iI][dD]\b'
    LET         = r'\b[lL][eE][tT]\b'
    LOOP        = r'\b[lL][oO][oO][pP]\b'
    NEW         = r'\b[nN][eE][wW]\b'
    OF          = r'\b[oO][fF]\b'
    POOL        = r'\b[pP][oO][oO][lL]\b'
    THEN        = r'\b[tT][hH][eE][nN]\b'
    WHILE       = r'\b[wW][hH][iI][lL][eE]\b'

    TYPEID      = r'([A-Z]([a-zA-Z0-9_])*)+'

    LE          = r'[<][=]'

    ASSIGN      = r'\b[<][-]\b'

    INT_CONST   = r'[0-9]+'

    @_(r'\n')
    def SALTO_LINEA(self, t):
        self.lineno += 1

    @_(r'\s+')
    def ESPACIO(self, t):
        pass

    @_(r'\b[f][aA][lL][sS][eE]\b|\b[t][rR][uU][eE]\b')
    def BOOL_CONST(self, t):
        if t.value[0] == 't':
            t.value = True
        else:
            t.value = False
        return t

    OBJECTID    = r'([a-z]([a-zA-Z0-9_])*)+'

    @_(r'"')
    def caracter(self, t):
        self.begin(String)

    @_(r'=>')
    def darrow(self, t):
        t.value = ''
        t.type = 'DARROW'
        return t

    @_(r'<-')
    def assign(self, t):
        t.value = ''
        t.type = 'ASSIGN'
        return t

    @_(r'[_]|[!]|[#]|[$]|[%]|[&]|[>]|[?]|[`]|[[]|[]]|[\\]|[|]|[\^]|[\\x*[a-zA-Z0-9]+]|[]|[]|[]|[]')
    def ERROR(self, t):
        if t.value == '\\':
            t.value = '\\\\'
        elif t.value == '':
            t.value = '\\001'
        elif t.value == '':
            t.value = '\\002'
        elif t.value == '':
            t.value = '\\003'
        elif t.value == '':
            t.value = '\\004'
        return t

    @_(r'--.*')
    def CMT_CONST1(self, t):
        pass

    @_(r'\(\*')
    def CMT_CONST(self, t):
        self.begin(Comment)

    @_(r'\*\)')
    def CMT_CONST_UNMATCHED(self, t):
        t.value = "Unmatched *)"
        t.type = 'ERROR'
        return t

    CARACTERES_CONTROL = [bytes.fromhex(i+hex(j)[-1]).decode('ascii')
                          for i in ['0', '1']
                          for j in range(16)] + [bytes.fromhex(hex(127)[-2:]).decode("ascii")]


    def salida(self, texto):
        list_strings = []
        lexer = CoolLexer()
        for token in lexer.tokenize(texto):
            result = f'#{token.lineno} {token.type} '
            if token.type == 'OBJECTID':
                result += f"{token.value}"
            elif token.type == 'BOOL_CONST':
                result += "true" if token.value else "false"
            elif token.type == 'TYPEID':
                result += f"{str(token.value)}"
            elif token.type in self.literals:
                result = f'#{token.lineno} \'{token.type}\''
            elif token.type == 'STR_CONST':
                result += token.value
            elif token.type == 'INT_CONST':
                result += str(token.value)
            elif token.type == 'ERROR':
                result = f'#{token.lineno} {token.type} "{token.value}"'
            else:
                result = f'#{token.lineno} {token.type}'
            list_strings.append(result)
        return list_strings

class String(Lexer):

    tokens = {STR_CONST, ERROR}
    _caracteres = ''
    nullchar_error = False

    @_(r'"')
    def STR_CONST(self, t):
        if self.nullchar_error:
            t.value = "String contains escaped null character."
            t.type = "ERROR"
        else:
            t.value = self._caracteres
            self._caracteres = ''
            self.begin(CoolLexer)
            t.value = '"' + t.value + '"'
        return t

    @_(r'\\\x00')
    def activa_error_nullchar_str(self, t):
        self.nullchar_error = True

    @_(r'\\\\')
    def doble_barra(self, t):
        self._caracteres += t.value[0:]

    @_(r'\\\n$')
    def salto_linea_escapado_y_EOF(self, t):
        t.value = "EOF in string constant"
        t.type = 'ERROR'
        return t

    @_(r'\\\n')
    def salto_linea_escapado(self, t):
        self._caracteres += '\\n'
        self.lineno += 1

    @_(r'\\.')
    def caracter_escapado(self, t):
        dic = defaultdict(lambda: t.value[1])
        dic['\\b'] = '\\b'
        dic['\\t'] = '\\t'
        dic['\\f'] = '\\f'
        dic['\\n'] = '\\n'
        dic['\\"'] = '\\"'

        self._caracteres += dic[t.value]

    @_(r'\n')
    def salto_linea_error(self, t):
        if not self.nullchar_error:
            self._caracteres = ''
            self.begin(CoolLexer)
            t.value = "Unterminated string constant"
            t.type = 'ERROR'
            return t

    @_(r'\t')
    def tabulador(self, t):
        self._caracteres += '\\t'

    @_(r'.$')
    def EOF_STR(self, t):
        t.value = "EOF in string constant"
        t.type = 'ERROR'
        return t

    @_(r'.')
    def caracter(self, t):
        self._caracteres += t.value

class Comment(Lexer):
    tokens = {CMT_CONST}
    cmt_id = 0

    @_(r'\*\)')
    def CMT_CONST(self, t):
        if self.cmt_id == 0:
            self.begin(CoolLexer)
        else:
            self.cmt_id -= 1

    @_(r'\(\*')
    def inside_CMT_CONST(self, t):
        self.cmt_id += 1

    @_(r'\n')
    def salto_linea(self, t):
        self.lineno += 1

    @_(r'.$')
    def EOF_CMT(self, t):
        t.value = "EOF in comment"
        t.type = 'ERROR'
        return t

    @_(r'.')
    def caracter(self, t):
        pass


