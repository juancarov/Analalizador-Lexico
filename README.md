# Analizador-Lexico

### Descripción General

El objetivo de este proyecto es desarrollar un analizador sintáctico del lenguaje Python en su versión simplificada, sin usar librerías externas como PLY o ANTLR.

El programa recibe un archivo de entrada con código fuente (.txt), realiza el análisis léxico y sintáctico, y genera una linea de texto con el resultado del proceso.

El sistema detecta errores sintácticos en el código y los reporta en el formato exigido por el profesor:

<pre><línea,col> Error sintactico: se encontro: "token_incorrecto"; se esperaba: "token_esperado".</pre>

Si el análisis finaliza correctamente, el resultado es:

<pre>El analisis sintactico ha finalizado exitosamente.</pre>

### Definición de Componentes

#### Análisis Lexico 

El analizador léxico es la primera parte del compilador.
Su función es recorrer el texto carácter por carácter, separando palabras, símbolos, operadores y números en una lista de tokens.

Cada token contiene su texto, línea y columna, lo que permite ubicar errores con precisión.

En este proyecto se implementa con la función separar_tokens()

```python
def separar_tokens(texto):
    tokens = []
    palabra = ""
    linea = 1
    columna = 1
    pos = 0
    while pos < len(texto):
        caracter = texto[pos]
        if caracter == "\n":
            linea += 1
            columna = 1
            if palabra:
                tokens.append((palabra, linea, columna))
                palabra = ""
            pos += 1
            continue
        if caracter in [" ", "\t"]:
            if palabra:
                tokens.append((palabra, linea, columna))
                palabra = ""
            columna += 1
            pos += 1
            continue
        if texto[pos:pos+2] in ["==", "!=", "<=", ">=", "**", "//"]:
            if palabra:
                tokens.append((palabra, linea, columna))
                palabra = ""
            tokens.append((texto[pos:pos+2], linea, columna))
            columna += 2
            pos += 2
            continue
        if caracter in SIMBOLOS:
            if palabra:
                tokens.append((palabra, linea, columna))
                palabra = ""
            tokens.append((caracter, linea, columna))
            columna += 1
            pos += 1
            continue
        palabra += caracter
        columna += 1
        pos += 1
    if palabra:
        tokens.append((palabra, linea, columna))
    tokens.append(("EOF", linea, columna))
    return tokens
```

Explicación

- Recorre el texto sin usar expresiones regulares.
- Detecta palabras reservadas, operadores y delimitadores.
- Guarda la posición del error si ocurre.
- Agrega un token final "EOF" para marcar el fin del archivo.

#### Análisis Sintáctico

El analizador sintáctico revisa si la secuencia de tokens cumple con las reglas gramaticales del lenguaje.
Se implementa mediante la clase Analizador, que usa métodos recursivos para validar estructuras como funciones, ciclos, condicionales, clases, expresiones, etc.

```python
class Analizador:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    def actual(self):
        return self.tokens[self.pos][0]
    def linea(self):
        return self.tokens[self.pos][1]
    def columna(self):
        return self.tokens[self.pos][2]
    def avanzar(self):
        self.pos += 1
    def coincidir(self, esperado):
        if self.actual() == esperado:
            self.avanzar()
        else:
            raise Exception(f'<{self.linea()},{self.columna()}> Error sintactico: se encontro: "{self.actual()}"; se esperaba: "{esperado}".')
    def programa(self):
        while self.actual() != "EOF":
            self.sentencia()
    def sentencia(self):
        token = self.actual()
        if token == "def":
            self.def_funcion()
        elif token == "class":
            self.def_clase()
        elif token == "if":
            self.condicional()
        elif token == "for":
            self.ciclo_for()
        elif token == "while":
            self.ciclo_while()
        elif token == "print" or token == "input":
            self.sentencia_funcion()
        elif token == "return":
            self.sentencia_return()
        elif token.isidentifier():
            self.expresion()
        elif token == "EOF":
            return
        else:
            raise Exception(f'<{self.linea()},{self.columna()}> Error sintactico: se encontro: "{token}"; se esperaba: "def", "class", "if", "for", "while", "print", "input" o "return".')
```

Explicación:

- Cada método valida un tipo de instrucción.
- Si algo no coincide, genera un error con la posición exacta.
- El programa se detiene en el primer error.

#### Reglas Gramaticales

PROGRAMA   → SENTENCIA*
SENTENCIA   → DEF_FUNCION | CLASE | IF | FOR | WHILE | PRINT | INPUT | RETURN | EXPRESION
DEF_FUNCION   → "def" ID "(" PARAMS ")" ":" SENTENCIA
CLASE   → "class" ID ( "(" EXPRESION ")" )? ":" SENTENCIA
IF   → "if" EXPRESION ":" SENTENCIA ( "elif" EXPRESION ":" SENTENCIA )* ( "else" ":" SENTENCIA )?
FOR   → "for" ID "in" EXPRESION ":" SENTENCIA
WHILE   → "while" EXPRESION ":" SENTENCIA
EXPRESION   → ID | NUM | (EXPRESION OPERADOR EXPRESION) | (EXPRESION) | [LISTA] | {DICCIONARIO}

Estas reglas representan una versión reducida de la gramática de Python.
Se permite el uso de expresiones aritméticas, listas, diccionarios y estructuras de control.
