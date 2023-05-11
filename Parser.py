# coding: utf-8

from Lexer import CoolLexer
from sly import Parser
import sys
import os
from Clases import *


class CoolParser(Parser):
    nombre_fichero = ''
    tokens = CoolLexer.tokens
    literals = CoolLexer.literals
    debugfile = "salida.out"
    errores = []

    precedence = (
        ('right', "ASSIGN"),
        ('left', "NOT"),
        ('left', "+", "-"),
        ('left', "*", "/"),
        ('left', "ISVOID"),
    )

    # PROGRAM
    @_('clases')
    def programa(self, p):
        return Programa(
            linea = p.lineno,
            secuencia =p.clases
        )

    # CLASS
    @_('clases clase ";"')
    def clases(self, p):
        p.clases.append(p.clase)
        return p.clases

    @_('clase ";"')
    def clases(self, p):
        return [p.clase]

    @_('CLASS TYPEID INHERITS TYPEID "{" "}"')
    def clase(self, p):
        return Clase(
            linea = p.lineno,
            nombre = p.TYPEID0,
            padre = p.TYPEID1,
            nombre_fichero = self.nombre_fichero,
            caracteristicas = []
        )

    @_('CLASS TYPEID INHERITS TYPEID "{" features "}"')
    def clase(self, p):
        return Clase(
            linea = p.lineno,
            nombre = p.TYPEID0,
            padre = p.TYPEID1,
            nombre_fichero = self.nombre_fichero,
            caracteristicas = p.features
        )

    @_('CLASS TYPEID "{" "}"')
    def clase(self, p):
        return Clase(
            linea = p.lineno,
            nombre = p.TYPEID,
            padre = "Object",
            nombre_fichero = self.nombre_fichero,
            caracteristicas = []
        )

    @_('CLASS TYPEID "{" features "}"')
    def clase(self, p):
        return Clase(
            linea = p.lineno,
            nombre = p.TYPEID,
            padre = "Object",
            nombre_fichero = self.nombre_fichero,
            caracteristicas = p.features
        )

    # FEATURE
    @_('features feature ";"')
    def features(self, p):
        p.features.append(p.feature)
        return p.features

    @_('feature ";"')
    def features(self, p):
        return [p.feature]

    @_('OBJECTID "(" formales ")" ":" TYPEID "{" expr "}"')
    def feature(self, p):
        return Metodo(
            linea = p.lineno,
            nombre = p.OBJECTID,
            tipo = p.TYPEID,
            cuerpo = p.expr,
            formales = p.formales
        )

    @_('OBJECTID "(" ")" ":" TYPEID "{" expr "}"')
    def feature(self, p):
        return Metodo(
            linea = p.lineno,
            nombre = p.OBJECTID,
            tipo = p.TYPEID,
            cuerpo = p.expr,
            formales = []
        )

    @_('OBJECTID ":" TYPEID')
    def feature(self, p):
        return Atributo(
            linea = p.lineno,
            nombre = p.OBJECTID,
            tipo = p.TYPEID,
            cuerpo = NoExpr()
        )

    @_('OBJECTID ":" TYPEID ASSIGN expr')
    def feature(self, p):
        return Atributo(
            linea = p.lineno,
            nombre = p.OBJECTID,
            tipo = p.TYPEID,
            cuerpo = p.expr
        )


    # FORMAL
    @_('"(" formales ")"')
    def formal(self, p):
        return p.formales

    @_('formales "," formal')
    def formales(self, p):
        p.formales.append(p.formal)
        return p.formales

    @_('formal')
    def formales(self, p):
        return [p.formal]

    @_('OBJECTID ":" TYPEID')
    def formal(self, p):
        return Formal(
            linea = p.lineno,
            nombre_variable = p.OBJECTID,
            tipo = p.TYPEID
        )

    # EXPR
    @_('OBJECTID ASSIGN expr')
    def expr(self, p):
        return Asignacion(
            linea = p.lineno,
            nombre = p.OBJECTID,
            cuerpo = p.expr
        )


    @_('exprs_add "," expr')
    def exprs_add(self, p):
        p.exprs_add.append(p.expr)
        return p.exprs_add

    @_('expr')
    def exprs_add(self, p):
        return [p.expr]

    @_('expr "." OBJECTID "(" ")" ')
    def expr(self, p):
        return LlamadaMetodoEstatico(
            linea = p.lineno,
            cuerpo = p.expr,
            clase = '_no_type',
            nombre_metodo = p.OBJECTID,
            argumentos = []
        )

    @_('expr "." OBJECTID "(" exprs_add ")" ')
    def expr(self, p):
        return LlamadaMetodoEstatico(
            linea = p.lineno,
            cuerpo = p.expr,
            clase = '_no_type',
            nombre_metodo = p.OBJECTID,
            argumentos = p.exprs_add
        )

    @_('expr "@" TYPEID "." OBJECTID "(" ")" ')
    def expr(self, p):
        return LlamadaMetodoEstatico(
            linea = p.lineno,
            cuerpo = p.expr,
            clase = p.TYPEID,
            nombre_metodo = p.OBJECTID,
            argumentos = []
        )

    @_('expr "@" TYPEID "." OBJECTID "(" exprs_add ")" ')
    def expr(self, p):
        return LlamadaMetodoEstatico(
            linea = p.lineno,
            cuerpo = p.expr,
            clase = p.TYPEID,
            nombre_metodo = p.OBJECTID,
            argumentos = p.exprs_add
        )

    @_('OBJECTID "(" ")"')
    def expr(self, p):
        return LlamadaMetodo(
            linea = p.lineno,
            cuerpo = Objeto('self'),
            nombre_metodo = p.OBJECTID,
            argumentos = []
        )

    @_('OBJECTID "(" exprs_add ")"')
    def expr(self, p):
        return LlamadaMetodo(
            linea = p.lineno,
            cuerpo = Objeto('self'),
            nombre_metodo = p.OBJECTID,
            argumentos = p.exprs_add
        )

    @_('IF expr THEN expr ELSE expr FI')
    def expr(self, p):
        return Condicional(
            linea = p.lineno,
            condicion = p.expr0,
            verdadero = p.expr1,
            falso = p.expr2
        )

    @_('WHILE expr LOOP expr POOL')
    def expr(self, p):
        return Bucle(
            linea = p.lineno,
            condicion = p.expr0,
            cuerpo = p.expr1
        )

    @_('exprs expr ";"')
    def exprs(self, p):
        p.exprs.append(p.expr)
        return p.exprs

    @_('expr ";"')
    def exprs(self, p):
        return [p.expr]

    @_('"{" exprs "}"')
    def expr(self, p):
       return Bloque(
            linea = p.lineno,
            expresiones = p.exprs
        )

    @_('inicializacion "," inicializaciones')
    def inicializaciones(self, p):
        p.inicializaciones.append(p.inicializacion)
        return p.inicializaciones

    @_('inicializacion')
    def inicializaciones(self, p):
        return [p.inicializacion]

    @_('OBJECTID ":" TYPEID')
    def inicializacion(self, p):
        return [p.OBJECTID, p.TYPEID, NoExpr()]

    @_('OBJECTID ":" TYPEID ASSIGN expr')
    def inicializacion(self, p):
        return [p.OBJECTID, p.TYPEID, p.expr]


    @_('LET inicializaciones IN expr')
    def expr(self, p):
        cuerpo = p.expr
        for inicializacion in p.inicializaciones:
            cuerpo = Let(
                linea = p.lineno,
                nombre = inicializacion[0],
                tipo = inicializacion[1],
                inicializacion = inicializacion[2],
                cuerpo = cuerpo
            )
        return cuerpo

    @_('CASE expr OF ramaCases ESAC')
    def expr(self, p):
        return Swicht(
            linea = p.lineno,
            expr = p.expr,
            casos = p.ramaCases
        )

    @_('OBJECTID ":" TYPEID DARROW expr')
    def ramaCase(self, p):
        return RamaCase(
            linea = p.lineno,
            nombre_variable = p.OBJECTID,
            tipo = p.TYPEID,
            cuerpo = p.expr
        )

    @_('ramaCases ramaCase ";"')
    def ramaCases(self, p):
        p.ramaCases.append(RamaCase)
        return p.ramaCases

    @_('ramaCase ";"')
    def ramaCases(self, p):
        return [p.ramaCase]

    @_('NEW TYPEID')
    def expr(self, p):
        return Nueva(
            linea = p.lineno,
            tipo = p.TYPEID
        )

    @_('ISVOID expr')
    def expr(self, p):
        return EsNulo(
            linea = p.lineno,
            expr = p.expr
        )

    @_('expr "+" expr')
    def expr(self, p):
        return Suma(
            linea = p.lineno,
            izquierda = p.expr0,
            derecha = p.expr1
        )

    @_('expr "-" expr')
    def expr(self, p):
        return Resta(
            linea = p.lineno,
            izquierda = p.expr0,
            derecha = p.expr1
        )

    @_('expr "*" expr')
    def expr(self, p):
        return Multiplicacion(
            linea = p.lineno,
            izquierda = p.expr0,
            derecha = p.expr1
        )

    @_('expr "/" expr')
    def expr(self, p):
        return Division(
            linea = p.lineno,
            izquierda = p.expr0,
            derecha = p.expr1
        )

    @_('"~" expr')
    def expr(self, p):
        return Neg(
            linea = p.lineno,
            expr = p.expr
        )

    @_('expr "<" expr')
    def expr(self, p):
        return Menor(
            linea = p.lineno,
            izquierda = p.expr0,
            derecha = p.expr1
        )

    @_('expr LE expr')
    def expr(self, p):
        return LeIgual(
            linea = p.lineno,
            izquierda = p.expr0,
            derecha = p.expr1
        )

    @_('expr "=" expr')
    def expr(self, p):
        return Igual(
            linea = p.lineno,
            izquierda = p.expr0,
            derecha = p.expr1
        )

    @_('NOT expr')
    def expr(self, p):
        return Not(
            linea = p.lineno,
            expr = p.expr
        )

    @_('( expr )')
    def expr(self, p):
        return Expresion(
            linea = p.lineno
        )

    @_('OBJECTID')
    def expr(self, p):
        return Objeto(
            linea = p.lineno,
            nombre = p.OBJECTID
        )

    @_('INT_CONST')
    def expr(self, p):
        return Entero(
            linea = p.lineno,
            valor = p.INT_CONST
        )

    @_('STR_CONST')
    def expr(self, p):
        return String(
            linea = p.lineno,
            valor = p.STR_CONST
        )

    @_('BOOL_CONST')
    def expr(self, p):
        return Booleano(
            linea = p.lineno,
            valor = p.BOOL_CONST
        )