# coding: utf-8
from dataclasses import dataclass, field
from typing import List


class Ambito:
    lista_ambitos = [dict()]
    lista_attr = [dict()]
    lista_meth = [dict()]
    var = True

    def new_scope(self):
        if len(self.lista_ambitos) == 0:
            pass
        else:
            self.lista_ambitos.append([dict(self.lista_ambitos[-1])])

    def end_scope(self):
        self.lista_ambitos.pop()

    def add_simbol(self, variable, tipo):
        self.lista_ambitos[-1][variable] = tipo

    def find_simbol(self, variable):
        return self.lista_ambitos[-1][variable]

    def add_method(self, nombre_carcateristica, nombre_clase, formales, tipo):
        self.lista_meth[nombre_carcateristica] = (nombre_clase, tipo)

    def add_attr(self, nombre_carcateristica, nombre_clase, tipo):
        self.lista_attr[nombre_carcateristica] = (nombre_clase, tipo)

    #? solo para definiciones de 'cosas' (clases, varaibles, objetos....)
    def check_scope(self, variable):
        if variable in self.lista_ambitos[-1]:
            return True
        else:
            return False

    def mca(self, A, B):
        if A == B:
            return A
        elif self.es_hijo(A, B):
            return B
        elif self.es_hijo(B, A):
            return A
        else:
            if self.var and A != Objeto:
                self.var = False
                self.mca(self.padre(A), B)
            elif not self.var and B != Objeto:
                self.var = True
                self.mca(A, self.padre(B))
            elif A == Objeto:
                self.mca(A, self.padre(B))
            else:
                self.mca((self.padre(A), B))

    def padre(self, A):
        return A.padre

    def es_hijo(self, A, B):
        if self.padre(A) == B:
            return True
        else:
            return False

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
        self.cast = self.cuerpo.cast


#TODO comprobar que los tipos de la llamada coinciden con los tipos que te pide la definicion del metodo
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

    #TODO preguntar si esta bien
    def Tipo(self, Ambito):

        if self.cuerpo.cast == self.clase:
            self.cast = self.cuerpo.cast
        else:
            raise Exception('llamadaMetodoEstatico devuelve mal tipo')


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

    #TODO
    def Tipo(self, Ambito):
        self.cast = self.cuerpo.cast


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

        #TODO hay que cambiarlo entero para que dependa del arbol y termine devolviendo object
        if self.condicion.cast == 'True':
            self.cast = Ambito.find_symbol(self.verdadero)
        else:
            self.cast = Ambito.find_symbol(self.falso)


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

    #TODO No se si esto esta bien
    def Tipo(self, Ambito):
        Ambito.new_scope()
        Ambito.add_simbol(self.nombre, self.tipo)
        Ambito.end_scope()

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

    #TODO hay que checkear los tipos
    def Tipo(self, Ambito):
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

    #TODO No se si esto esta bien
    def Tipo(self, Ambito):
        self.cast = self.tipo


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
    #TODO creo que no tiene tipo

@dataclass
class Nueva(Nodo):
    tipo: str = '_no_set'
    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_new\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    #TODO No se si esto esta bien
    def Tipo(self, Ambito):
        self.cast = self.tipo

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
        if self.izquierda.cast == self.derecha.cast and self.derecha.cast == 'int':
            self.cast = 'int'
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
        if self.izquierda.cast == self.derecha.cast and self.derecha.cast == 'int':
            self.cast = 'int'
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
        if self.izquierda.cast == self.derecha.cast and self.derecha.cast == 'int':
            self.cast = 'int'
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
        if self.izquierda.cast == self.derecha.cast and self.derecha.cast == 'int':
            self.cast = 'int'
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
            self.cast = 'bool'
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
            self.cast = 'bool'
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
            self.cast = 'bool'
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
        self.cast = "INT_CONST"


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
        self.cast = "STR_CONST"

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
        self.cast = "BOOL"

@dataclass
class IterableNodo(Nodo):
    secuencia: List = field(default_factory=List)

#TODO ademas tendremos que hacer algo asi como lo de abrir scope o algo asi

class Programa(IterableNodo):
    def str(self, n):
        resultado = super().str(n)
        resultado += f'{" "*n}_program\n'
        resultado += ''.join([c.str(n+2) for c in self.secuencia])
        return resultado

    def tipo(self):
        ambito = Ambito()
        for clase in self.secuencia:
            ambito.add_class(clase.nombre, clase.padre)
            for caracteristica in clase.caracteristicas:
                if isinstance(caracteristica, Metodo):
                    ambito.add_method(caracteristica.nombre, clase.nombre, caracteristica.formales, caracteristica.tipo)
                else:
                    ambito.add_attr(caracteristica.nombre, clase.nombre, caracteristica.tipo)

        for clase in self.secuencia:
            clase.tipo(ambito)

@dataclass
class Caracteristica(Nodo):
    nombre: str = '_no_set'
    tipo: str = '_no_set'
    cuerpo: Expresion = None

    def Tipo(self, Ambito):
        self.cast = self.tipo


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
        resultado += f'{(n+2)*" "})\n'
        return resultado

    #TODO chequear
    #TODO puede ser caracteristica.cast
    def Tipo(self, Ambito):
        Ambito.new_scope()
        for caracteristica in self.caracteristicas:
            Ambito.add_simbol(caracteristica.OBJECTID, caracteristica.TYPEID)
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

    def Tipo(self, Ambito):
        Ambito.new_scope()
        for formal in self.formales:
            Ambito.add_simbol(formal.OBJECTID, formal.TYPEID)
        self.cuerpo.Tipo(Ambito)
        if not Ambito.eshijo(self.tipo, self.cuerpo.cast):
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
