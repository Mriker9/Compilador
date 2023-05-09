# coding: utf-8
from dataclasses import dataclass, field
from typing import List

#TODO como hacer bien el stack(ejemplo en Objeto linea 520)
#TODO mirar Programa, Clase y metodo
#TODO mirar los fallos de ejecución
#TODO mirar expresion y si cuerpo.Tipo(Ambito) esta bien
#TODO checkear condicional
#TODO mirar si el switch tiene tipo
#TODO tipo de objeto y noExpr

class Ambito:
    stack = [dict()]
    lista_pdr = dict({'Int': 'Object', 'String': 'Object', 'Bool': 'Object', 'IO': 'Object', 'Object': 'Object'})
    lista_attr = dict()
    lista_meth = dict()

    def new_scope(self):
        self.stack.append(dict())

    def end_scope(self):
        self.stack.pop()

    def check_scope(self, variable):
        if variable in self.stack[-1]:
            return True
        else:
            return False

    def add_simbol(self, variable, tipo):
        self.stack[-1][variable] = tipo

    def pop_simbol(self, variable):
        self.stack[-1][variable].pop()

    def empty_stack(self):
        self.stack = [dict()]
        self.lista_pdr = dict()
        self.lista_attr = dict()
        self.lista_meth = dict()

    def find_simbol(self, variable):
        return self.stack[-1][variable]

    def add_padre(self, clase, padre):
        self.lista_pdr[clase] = padre

    def get_padre(self, clase):
        return self.lista_pdr[clase]

    def add_method(self, clase, metodo, formales, tipo):
        self.lista_meth[(clase, metodo)] = [formales, tipo]

    def get_method(self, clase, metodo):
        return self.lista_meth[(clase, metodo)]

    def add_attr(self, clase, attr, tipo):
        self.lista_attr[(clase, attr)] = tipo

    def get_attr(self, clase, attr):
        return self.lista_attr[(clase, attr)]

    def es_subtipo(self, A, B):
        if A == B:
            return True
        elif A == 'Object':
            return False
        else:
            return self.es_subtipo(self.get_padre(A), B)

    def mca(self, A, B):
        if 'Object' in [A, B]:
            return 'Object'
        if A == B:
            return A
        elif self.es_subtipo(A, B):
            return B
        elif self.es_subtipo(B, A):
            return A
        else:
            return self.mca(self.get_padre(A), self.get_padre(B))


@dataclass
class Nodo:
    linea: int = 0
    def str(self, n):
        return f'{n*" "}#{self.linea}\n'


@dataclass
class Formal(Nodo):
    nombre_variable: str = '_no_set'
    tipo: str = '_no_type'
    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_formal\n'
        resultado += f'{(n+2)*" "}{self.nombre_variable}\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        return resultado

    def Tipo(self, Ambito):
        self.cast = self.tipo


class Expresion(Nodo):
    cast: str = '_no_type'


@dataclass
class Asignacion(Expresion):
    nombre: str = '_no_set'
    cuerpo: Expresion = None

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_assign\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, Ambito):
        self.cuerpo.Tipo(Ambito)
        self.cast = self.cuerpo.cast


@dataclass
class LlamadaMetodoEstatico(Expresion):
    cuerpo: Expresion = None
    clase: str = '_no_type'
    nombre_metodo: str = '_no_set'
    argumentos: List[Expresion] = field(default_factory=list)


    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_static_dispatch\n'
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n+2)*" "}{self.clase}\n'
        resultado += f'{(n+2)*" "}{self.nombre_metodo}\n'
        resultado += f'{(n+2)*" "}(\n'
        resultado += ''.join([c.str(n+2) for c in self.argumentos])
        resultado += f'{(n+2)*" "})\n'
        resultado += f'{(n)*" "}: _no_type\n'
        return resultado

    def Tipo(self, Ambito):
        self.cuerpo.Tipo(Ambito)
        formales, tipo = Ambito.get_method(self.cuerpo.cast, self.nombre_metodo)
        for f, a in zip(formales, self.argumentos):
            a.Tipo(Ambito)
            if not Ambito.es_subtipo(a.cast, f.tipo):
                raise Exception('llamadametodoestatico con argumentos de mal tipo')

        if tipo != self.clase:
            raise Exception('llamadametodoestatico con mal tipo')
        else:
            self.cast = tipo


@dataclass
class LlamadaMetodo(Expresion):
    cuerpo: Expresion = None
    nombre_metodo: str = '_no_set'
    argumentos: List[Expresion] = field(default_factory=list)

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_dispatch\n'
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n+2)*" "}{self.nombre_metodo}\n'
        resultado += f'{(n+2)*" "}(\n'
        resultado += ''.join([c.str(n+2) for c in self.argumentos])
        resultado += f'{(n+2)*" "})\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, Ambito):
        self.cuerpo.Tipo(Ambito)
        formales, tipo = Ambito.get_method(self.cuerpo.cast, self.nombre_metodo)
        for f, a in zip(formales, self.argumentos):
            a.Tipo(Ambito)
            if not Ambito.es_subtipo(a.cast, f.tipo):
                raise Exception('llamaMetodo con argumentos con mal tipo')

        self.cast = tipo


@dataclass
class Condicional(Expresion):
    condicion: Expresion = None
    verdadero: Expresion = None
    falso: Expresion = None

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_cond\n'
        resultado += self.condicion.str(n+2)
        resultado += self.verdadero.str(n+2)
        resultado += self.falso.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, Ambito):
        self.condicion.Tipo(Ambito)
        self.verdadero.Tipo(Ambito)
        self.falso.Tipo(Ambito)

        if self.condicion.cast != 'BOOL':
            raise Exception('condición mal tipo')

        self.cast = Ambito.mca(self.verdadero.cast, self.falso.cast)


@dataclass
class Bucle(Expresion):
    condicion: Expresion = None
    cuerpo: Expresion = None

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_loop\n'
        resultado += self.condicion.str(n+2)
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, Ambito):
        self.cuerpo.Tipo(Ambito)
        self.cast = self.cuerpo.cast


@dataclass
class Let(Expresion):
    nombre: str = '_no_set'
    tipo: str = '_no_set'
    inicializacion: Expresion = None
    cuerpo: Expresion = None

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_let\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        resultado += self.inicializacion.str(n+2)
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, Ambito):
        Ambito.new_scope()
        Ambito.add_simbol(self.nombre, self.tipo)
        Ambito.end_scope()

        self.cuerpo.Tipo(Ambito)
        if self.cuerpo.cast == self.tipo:
            self.cast = self.tipo
        else:
            raise Exception('let con mal tipo')


@dataclass
class Bloque(Expresion):
    expresiones: List[Expresion] = field(default_factory=list)

    def str(self, n):
        resultado = super().str(n)
        resultado = f'{n*" "}_block\n'
        resultado += ''.join([e.str(n+2) for e in self.expresiones])
        resultado += f'{(n)*" "}: {self.cast}\n'
        resultado += '\n'
        return resultado

    def Tipo(self, Ambito):
        self.expresiones[-1].Tipo(Ambito)
        self.cast = self.expresiones[-1].cast


@dataclass
class RamaCase(Nodo):
    nombre_variable: str = '_no_set'
    tipo: str = '_no_set'
    cuerpo: Expresion = None

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_branch\n'
        resultado += f'{(n+2)*" "}{self.nombre_variable}\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, Ambito):
        self.cuerpo.Tipo(Ambito)
        if self.tipo == self.cuerpo.cast:
            self.cast = self.tipo
        else:
            raise Exception('mal tipo en ramacase')


@dataclass
class Swicht(Nodo):
    expr: Expresion = None
    casos: List[RamaCase] = field(default_factory=list)

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_typcase\n'
        resultado += self.expr.str(n+2)
        resultado += ''.join([c.str(n+2) for c in self.casos])
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

@dataclass
class Nueva(Nodo):
    tipo: str = '_no_set'
    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_new\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        #resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    '''
    def Tipo(self, Ambito):
        self.cast = self.tipo
    '''

@dataclass
class OperacionBinaria(Expresion):
    izquierda: Expresion = None
    derecha: Expresion = None


@dataclass
class Suma(OperacionBinaria):
    operando: str = '+'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_plus\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, Ambito):
        self.izquierda.Tipo(Ambito)
        self.derecha.Tipo(Ambito)
        if self.izquierda.cast == self.derecha.cast and self.derecha.cast == 'INT_CONST':
            self.cast = 'INT_CONST'
        else:
            raise Exception('operandos con distinto tipo en Suma')


@dataclass
class Resta(OperacionBinaria):
    operando: str = '-'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_sub\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, Ambito):
        self.izquierda.Tipo(Ambito)
        self.derecha.Tipo(Ambito)
        if self.izquierda.cast == self.derecha.cast and self.derecha.cast == 'INT_CONST':
            self.cast = 'INT_CONST'
        else:
            raise Exception('operandos con distinto tipo en Resta')


@dataclass
class Multiplicacion(OperacionBinaria):
    operando: str = '*'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_mul\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, Ambito):
        self.izquierda.Tipo(Ambito)
        self.derecha.Tipo(Ambito)
        if self.izquierda.cast == self.derecha.cast and self.derecha.cast == 'INT_CONST':
            self.cast = 'INT_CONST'
        else:
            raise Exception('operandos con distinto tipo en Multiplicacion')


@dataclass
class Division(OperacionBinaria):
    operando: str = '/'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_divide\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, Ambito):
        self.izquierda.Tipo(Ambito)
        self.derecha.Tipo(Ambito)
        if self.izquierda.cast == self.derecha.cast and self.derecha.cast == 'INT_CONST':
            self.cast = 'INT_CONST'
        else:
            raise Exception('operandos con distinto tipo en Division')


@dataclass
class Menor(OperacionBinaria):
    operando: str = '<'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_lt\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, Ambito):
        self.izquierda.Tipo(Ambito)
        self.derecha.Tipo(Ambito)
        if self.izquierda.cast == self.derecha.cast:
            self.cast = 'BOOL'
        else:
            raise Exception('operandos con distinto tipo en Menor')

@dataclass
class LeIgual(OperacionBinaria):
    operando: str = '<='

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_leq\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, Ambito):
        self.izquierda.Tipo(Ambito)
        self.derecha.Tipo(Ambito)
        if self.izquierda.cast == self.derecha.cast:
            self.cast = 'BOOL'
        else:
            raise Exception('operandos con distinto tipo en LeIgual')


@dataclass
class Igual(OperacionBinaria):
    operando: str = '='

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_eq\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


    def Tipo(self, Ambito):
        self.izquierda.Tipo(Ambito)
        self.derecha.Tipo(Ambito)
        if self.izquierda.cast == self.derecha.cast:
            self.cast = 'BOOL'
        else:
            raise Exception('operandos con distinto tipo en Igual')

@dataclass
class Neg(Expresion):
    expr: Expresion = None
    operador: str = '~'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_neg\n'
        resultado += self.expr.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, Ambito):
        self.expr.Tipo(Ambito)
        self.cast = self.expr.cast


@dataclass
class Not(Expresion):
    expr: Expresion = None
    operador: str = 'NOT'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_comp\n'
        resultado += self.expr.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, Ambito):
        self.expr.Tipo(Ambito)
        self.cast = self.expr.cast


@dataclass
class EsNulo(Expresion):
    expr: Expresion = None

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_isvoid\n'
        resultado += self.expr.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, Ambito):
        self.expr.Tipo(Ambito)
        self.cast = self.expr.cast


@dataclass
class Objeto(Expresion):
    nombre: str = '_no_set'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_object\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, Ambito):
        self.cast = Ambito.find_simbol(self.nombre)

@dataclass
class NoExpr(Expresion):
    nombre: str = ''

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_no_expr\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, Ambito):
        self.cast = Ambito.find_simbol(self.nombre)


@dataclass
class Entero(Expresion):
    valor: int = 0

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_int\n'
        resultado += f'{(n+2)*" "}{self.valor}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, Ambito):
        self.cast = "Int"


@dataclass
class String(Expresion):
    valor: str = '_no_set'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_string\n'
        resultado += f'{(n+2)*" "}{self.valor}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, Ambito):
        self.cast = "String"

@dataclass
class Booleano(Expresion):
    valor: bool = False

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_bool\n'
        resultado += f'{(n+2)*" "}{1 if self.valor else 0}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, Ambito):
        self.cast = "Bool"

@dataclass
class IterableNodo(Nodo):
    secuencia: List = field(default_factory=List)

class Programa(IterableNodo):
    def str(self, n):
        resultado = super().str(n)
        resultado += f'{" "*n}_program\n'
        resultado += ''.join([c.str(n+2) for c in self.secuencia])
        return resultado

    def Tipo(self):
        ambito = Ambito()
        for clase in self.secuencia:
            ambito.add_padre(clase.nombre, clase.padre)
            for caracteristica in clase.caracteristicas:
                if isinstance(caracteristica, Metodo):
                    ambito.add_method(clase.nombre, caracteristica.nombre, caracteristica.formales, caracteristica.tipo)
                else:
                    ambito.add_attr(clase.nombre, caracteristica.nombre, caracteristica.tipo)

        for clase in self.secuencia:
            clase.Tipo(ambito)

@dataclass
class Caracteristica(Nodo):
    nombre: str = '_no_set'
    tipo: str = '_no_set'
    cuerpo: Expresion = None

    def Tipo(self, Ambito):
        self.cuerpo.Tipo(Ambito)
        if self.tipo == self.cuerpo.cast:
            self.cast = self.tipo
        else:
            raise Exception('mal tipo caracteristicas')


@dataclass
class Clase(Nodo):
    nombre: str = '_no_set'
    padre: str = '_no_set'
    nombre_fichero: str = '_no_set'
    caracteristicas: List[Caracteristica] = field(default_factory=list)

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_class\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += f'{(n+2)*" "}{self.padre}\n'
        resultado += f'{(n+2)*" "}"{self.nombre_fichero}"\n'
        resultado += f'{(n+2)*" "}(\n'
        resultado += ''.join([c.str(n+2) for c in self.caracteristicas])
        resultado += '\n'
        resultado += f'{(n+2)*" "})\n'
        return resultado

    #TODO practica 4, es ir haciendo esto y se pone con es en python
    #TODO es como ir traduciendo
    def codigo(self, n):
        resultado += f'{(n) * " "} class {self.nombre}({self.padre}):\n'
        resultado += '\t'.join([c.str(n+2) for c in self.caracteristicas])
        resultado += '\n'
        #resultado += f'{(n+2)*" "})\n'
        return resultado

    def Tipo(self, Ambito):
        Ambito.new_scope()
        for caracteristica in self.caracteristicas:
            Ambito.add_simbol(caracteristica.nombre, caracteristica.tipo)
        for car in self.caracteristicas:
            car.Tipo(Ambito)
        Ambito.end_scope()

        self.cast = self.nombre

@dataclass
class Metodo(Caracteristica):
    formales: List[Formal] = field(default_factory=list)

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_method\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += ''.join([c.str(n+2) for c in self.formales])
        resultado += f'{(n + 2) * " "}{self.tipo}\n'
        resultado += self.cuerpo.str(n+2)
        return resultado

    '''
    def codigo(self, n):
        resultado += f'{(n) * " "} def {self.nombre}({[c.str(n) for c in self.formales]}):\n'
        resultado += self.cuerpo.str(n+1)
        resultado += '\n'
        return resultado
    '''

    def Tipo(self, Ambito):
        Ambito.new_scope()
        for formal in self.formales:
            Ambito.add_simbol(formal.nombre_variable, formal.tipo)
        self.cuerpo.Tipo(Ambito)

        if not Ambito.es_subtipo(self.tipo, self.cuerpo.cast):
            raise Exception('error de tipos en Metodo')
        Ambito.end_scope()


class Atributo(Caracteristica):

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_attr\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        resultado += self.cuerpo.str(n+2)
        return resultado

    def Tipo(self, Ambito):
        if self.nombre == 'self':
            raise Exception(f'{self.linea}: \'self\' cannot be the name of an attribute.')
        else:
            self.cast = Ambito.find_simbol(self.nombre)
