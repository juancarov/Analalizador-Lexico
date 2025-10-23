PALABRAS = [
    "def", "class", "if", "elif", "else", "for", "in", "while",
    "return", "break", "continue", "pass", "print", "input",
    "and", "or", "not", "True", "False", "None",
    "try", "except", "finally", "with", "as", "import", "from",
    "global", "nonlocal", "lambda", "yield", "raise", "assert",
    "is", "del", "await", "async"
]

SIMBOLOS = [
    "(", ")", "[", "]", "{", "}", ":", ",", ".", ";",
    "=", "+", "-", "*", "/", "%", "<", ">", "!", "==", "!=", "<=", ">=", "**", "//"
]

def separar_tokens(texto):
    tokens = []
    palabra = ""
    linea = 1
    columna = 1
    pos = 0
    while pos < len(texto):
        caracter = texto[pos]

        # Salto de línea
        if caracter == "\n":
            linea += 1
            columna = 1
            if palabra:
                tokens.append((palabra, linea, columna))
                palabra = ""
            pos += 1
            continue

        # Espacio o tabulación
        if caracter in [" ", "\t"]:
            if palabra:
                tokens.append((palabra, linea, columna))
                palabra = ""
            columna += 1
            pos += 1
            continue

        # Cadenas entre comillas simples o dobles
        if caracter in ['"', "'"]:
            comilla = caracter
            inicio_col = columna
            cadena = comilla
            pos += 1
            columna += 1
            while pos < len(texto) and texto[pos] != comilla:
                if texto[pos] == "\n":
                    linea += 1
                    columna = 1
                cadena += texto[pos]
                pos += 1
                columna += 1
            if pos < len(texto):
                cadena += comilla
                pos += 1
                columna += 1
            else:
                raise Exception(f'<{linea},{inicio_col}> Error sintactico: cadena sin cerrar.')
            tokens.append((cadena, linea, inicio_col))
            palabra = ""
            continue

        # Operadores dobles
        if texto[pos:pos+2] in ["==", "!=", "<=", ">=", "**", "//"]:
            if palabra:
                tokens.append((palabra, linea, columna))
                palabra = ""
            tokens.append((texto[pos:pos+2], linea, columna))
            columna += 2
            pos += 2
            continue

        # Símbolos individuales
        if caracter in SIMBOLOS:
            if palabra:
                tokens.append((palabra, linea, columna))
                palabra = ""
            tokens.append((caracter, linea, columna))
            columna += 1
            pos += 1
            continue

        # Acumular palabra o número
        palabra += caracter
        columna += 1
        pos += 1

    if palabra:
        tokens.append((palabra, linea, columna))
    tokens.append(("EOF", linea, columna))
    return tokens


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
        elif token == "elif" or token == "else":
            self.avanzar()
            self.coincidir(":")
            self.sentencia()
        elif token == "for":
            self.ciclo_for()
        elif token == "while":
            self.ciclo_while()
        elif token == "try":
            self.bloque_try()
        elif token == "except" or token == "finally":
            self.avanzar()
            if self.actual() == ":":
                self.avanzar()
                self.sentencia()
        elif token == "print" or token == "input":
            self.sentencia_funcion()
        elif token == "return":
            self.sentencia_return()
        elif token == "pass":
            self.avanzar()
        elif token == "break" or token == "continue":
            self.avanzar()
        elif token.isidentifier():
            self.sentencia_asignacion_o_expresion()
        elif token == "EOF":
            return
        else:
            raise Exception(f'<{self.linea()},{self.columna()}> Error sintactico: se encontro: "{token}"; se esperaba: "def", "class", "if", "elif", "else", "for", "while", "print", "input" o "return".')

    def sentencia_asignacion_o_expresion(self):
        nombre = self.actual()
        self.avanzar()
        if self.actual() == "=":
            self.avanzar()
            self.expresion()
        elif self.actual() in ["+", "-", "*", "/", "%", "==", "!=", "<=", ">=", "<", ">", "and", "or"]:
            self.avanzar()
            self.expresion()
        else:
            return

    def def_funcion(self):
        self.coincidir("def")
        nombre = self.actual()
        if not nombre.isidentifier():
            raise Exception(f'<{self.linea()},{self.columna()}> Error sintactico: se encontro: "{nombre}"; se esperaba: "nombre de funcion".')
        self.avanzar()
        self.coincidir("(")
        if self.actual() != ")":
            self.parametros()
        self.coincidir(")")
        self.coincidir(":")
        self.sentencia()

    def def_clase(self):
        self.coincidir("class")
        nombre = self.actual()
        if not nombre.isidentifier():
            raise Exception(f'<{self.linea()},{self.columna()}> Error sintactico: se encontro: "{nombre}"; se esperaba: "nombre de clase".')
        self.avanzar()
        if self.actual() == "(":
            self.avanzar()
            self.expresion()
            self.coincidir(")")
        self.coincidir(":")
        self.sentencia()

    def parametros(self):
        while True:
            nombre = self.actual()
            if not nombre.isidentifier():
                raise Exception(f'<{self.linea()},{self.columna()}> Error sintactico: se encontro: "{nombre}"; se esperaba: "identificador".')
            self.avanzar()
            if self.actual() == ",":
                self.avanzar()
                continue
            else:
                break

    def condicional(self):
        self.coincidir("if")
        self.expresion()
        self.coincidir(":")
        self.sentencia()
        while self.actual() == "elif":
            self.avanzar()
            self.expresion()
            self.coincidir(":")
            self.sentencia()
        if self.actual() == "else":
            self.avanzar()
            self.coincidir(":")
            self.sentencia()

    def ciclo_for(self):
        self.coincidir("for")
        variable = self.actual()
        if not variable.isidentifier():
            raise Exception(f'<{self.linea()},{self.columna()}> Error sintactico: se encontro: "{variable}"; se esperaba: "identificador".')
        self.avanzar()
        self.coincidir("in")
        self.expresion()
        self.coincidir(":")
        self.sentencia()

    def ciclo_while(self):
        self.coincidir("while")
        self.expresion()
        self.coincidir(":")
        self.sentencia()

    def bloque_try(self):
        self.coincidir("try")
        self.coincidir(":")
        self.sentencia()
        if self.actual() == "except":
            self.avanzar()
            if self.actual().isidentifier():
                self.avanzar()
            self.coincidir(":")
            self.sentencia()
        if self.actual() == "finally":
            self.avanzar()
            self.coincidir(":")
            self.sentencia()

    def sentencia_funcion(self):
        nombre = self.actual()
        self.avanzar()
        self.coincidir("(")
        if self.actual() != ")":
            self.expresion()
        self.coincidir(")")

    def sentencia_return(self):
        self.coincidir("return")
        if self.actual() not in [":", "EOF"]:
            self.expresion()

    def expresion(self):
        token = self.actual()
        if token.isidentifier() or token.isnumeric() or token in ["True", "False", "None"] or (
            (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'"))
        ):
            self.avanzar()
            if self.actual() in ["+", "-", "*", "/", "%", "==", "!=", "<=", ">=", "<", ">", "and", "or"]:
                self.avanzar()
                self.expresion()
        elif token == "(":
            self.avanzar()
            self.expresion()
            self.coincidir(")")
        elif token == "[":
            self.avanzar()
            if self.actual() != "]":
                self.expresion()
                while self.actual() == ",":
                    self.avanzar()
                    self.expresion()
            self.coincidir("]")
        elif token == "{":
            self.avanzar()
            if self.actual() != "}":
                self.expresion()
                self.coincidir(":")
                self.expresion()
            self.coincidir("}")
        else:
            raise Exception(f'<{self.linea()},{self.columna()}> Error sintactico: se encontro: "{token}"; se esperaba: "expresion valida".')


def analizar(nombre_archivo):
    try:
        with open(nombre_archivo, "r", encoding="utf-8") as archivo:
            codigo = archivo.read()
    except FileNotFoundError:
        print("No se encontro el archivo de entrada.")
        return
    try:
        tokens = separar_tokens(codigo)
        analizador = Analizador(tokens)
        analizador.programa()
        resultado = "El analisis sintactico ha finalizado exitosamente."
    except Exception as e:
        resultado = str(e)
    with open("salida.txt", "w", encoding="utf-8") as salida:
        salida.write(resultado + "\n")
    print(resultado)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Uso: python3 proyecto.py archivo.txt")
    else:
        analizar(sys.argv[1])
