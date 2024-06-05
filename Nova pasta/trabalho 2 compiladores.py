import re

class SymbolTable:
    def __init__(self):
        self.symbols = {}

    def add_symbol(self, token, lexema, tipo, valor=None):
        if lexema in self.symbols:
            raise ValueError(f"Variável '{lexema}' já declarada neste escopo.")
        self.symbols[lexema] = {'token': token, 'tipo': tipo, 'valor': valor}

    def get_symbol(self, lexema):
        return self.symbols.get(lexema, None)

    def update_symbol(self, lexema, valor):
        if lexema not in self.symbols:
            raise ValueError(f"Variável '{lexema}' não declarada neste escopo.")
        self.symbols[lexema]['valor'] = valor

    def __contains__(self, lexema):
        return lexema in self.symbols

    def __repr__(self):
        return str(self.symbols)


class SemanticAnalyzer:
    def __init__(self, entrada):
        self.entrada = entrada
        self.escopo_pilha = []
        self.current_scope = None
        self.output = []
        self.linha_atual = 0

    def push_scope(self, nome):
        new_scope = SymbolTable()
        self.escopo_pilha.append(new_scope)
        self.current_scope = new_scope

    def pop_scope(self):
        self.escopo_pilha.pop()
        self.current_scope = self.escopo_pilha[-1] if self.escopo_pilha else None

    def analyze(self):
        for line in self.entrada:
            self.linha_atual += 1
            line = line.strip()
            if line.startswith('BLOCO'):
                nome_bloco = line.split('BLOCO')[-1].strip()
                self.push_scope(nome_bloco)
            elif line.startswith('FIM'):
                self.pop_scope()
            elif line.startswith('NUMERO') or line.startswith('CADEIA'):
                self.handle_declaration(line)
            elif line.startswith('PRINT'):
                self.handle_print(line)
            else:
                self.handle_assignment(line)

    def handle_declaration(self, line):
        tipo, restante = line.split(' ', 1)
        declarations = [x.strip() for x in restante.split(',')]
        for decl in declarations:
            if '=' in decl:
                lexema, valor = decl.split('=')
                lexema = lexema.strip()
                valor = valor.strip()
            else:
                lexema = decl.strip()
                valor = None
            self.current_scope.add_symbol('variável', lexema, tipo.lower(), valor)

    def handle_assignment(self, line):
        if '=' in line:
            lexema, valor = line.split('=')
            lexema = lexema.strip()
            valor = valor.strip()

            # Verificar se a variável à esquerda está declarada
            var_left = None
            for scope in reversed(self.escopo_pilha):
                if lexema in scope:
                    var_left = scope.get_symbol(lexema)
                    break
            if not var_left:
                self.output.append(f"Erro linha {self.linha_atual}, variável não declarada")
                return

            # Verificar se a variável ou constante à direita está declarada
            var_right = None
            if re.match(r'^[a-z_][a-z0-9_]*$', valor):
                for scope in reversed(self.escopo_pilha):
                    if valor in scope:
                        var_right = scope.get_symbol(valor)
                        valor = var_right['valor']
                        break
                if not var_right:
                    self.output.append(f"Erro linha {self.linha_atual}, variável não declarada")
                    return
                if var_left['tipo'] != var_right['tipo']:
                    self.output.append(f"Erro linha {self.linha_atual}, tipos não compatíveis")
                    return
            else:
                if var_left['tipo'] == 'numero' and not re.match(r'^[+-]?\d+(\.\d+)?$', valor):
                    self.output.append(f"Erro linha {self.linha_atual}, tipos não compatíveis")
                    return
                elif var_left['tipo'] == 'cadeia' and not re.match(r'^".*"$', valor):
                    self.output.append(f"Erro linha {self.linha_atual}, tipos não compatíveis")
                    return

            # Atualizar o valor da variável à esquerda
            for scope in reversed(self.escopo_pilha):
                if lexema in scope:
                    scope.update_symbol(lexema, valor)
                    break

    def handle_print(self, line):
        _, lexema = line.split(' ')
        lexema = lexema.strip()
        for scope in reversed(self.escopo_pilha):
            if lexema in scope:
                valor = scope.get_symbol(lexema)['valor']
                self.output.append(f"{valor}")
                break
        else:
            self.output.append(f"Erro linha {self.linha_atual}, variável não declarada")

    def get_output(self):
        return "\n".join(self.output)


# Leitura do arquivo e inicialização do analisador
with open("hello.cic", "r") as f:
    entrada = f.readlines()

analisador = SemanticAnalyzer(entrada)
analisador.analyze()

print(analisador.get_output())