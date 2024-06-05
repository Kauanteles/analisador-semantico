import re

# Classe que representa a tabela de símbolos para um escopo
class TabelaSimbolos:
    def __init__(self):
        self.simbolos = {}

    def adicionar_simbolo(self, token, lexema, tipo, valor=None):
        # Adiciona um símbolo na tabela de símbolos
        if lexema in self.simbolos:
            raise ValueError(f"Variável '{lexema}' já declarada neste escopo.")
        self.simbolos[lexema] = {'token': token, 'tipo': tipo, 'valor': valor}

    def obter_simbolo(self, lexema):
        # Retorna o símbolo pelo lexema, se existir
        return self.simbolos.get(lexema, None)

    def atualizar_simbolo(self, lexema, valor):
        # Atualiza o valor de um símbolo existente
        if lexema not in self.simbolos:
            raise ValueError(f"Variável '{lexema}' não declarada neste escopo.")
        self.simbolos[lexema]['valor'] = valor

    def __contains__(self, lexema):
        # Verifica se um lexema está na tabela de símbolos
        return lexema in self.simbolos

    def __repr__(self):
        # Representação em string da tabela de símbolos
        return str(self.simbolos)


# Classe que realiza a análise semântica do código
class AnalisadorSemantico:
    def __init__(self, entrada):
        self.entrada = entrada  # Linhas do código de entrada
        self.pilha_escopos = []  # Pilha de escopos
        self.escopo_atual = None  # Escopo atual
        self.saida = []  # Saída do analisador
        self.linha_atual = 0  # Contador de linhas

    def empurrar_escopo(self, nome):
        # Cria um novo escopo e adiciona à pilha
        novo_escopo = TabelaSimbolos()
        self.pilha_escopos.append(novo_escopo)
        self.escopo_atual = novo_escopo

    def remover_escopo(self):
        # Remove o escopo atual da pilha
        self.pilha_escopos.pop()
        self.escopo_atual = self.pilha_escopos[-1] if self.pilha_escopos else None

    def analisar(self):
        # Analisa linha por linha do código
        for linha in self.entrada:
            self.linha_atual += 1
            linha = linha.strip()
            if linha.startswith('BLOCO'):
                # Início de um novo bloco
                nome_bloco = linha.split('BLOCO')[-1].strip()
                self.empurrar_escopo(nome_bloco)
            elif linha.startswith('FIM'):
                # Fim de um bloco
                self.remover_escopo()
            elif linha.startswith('NUMERO') or linha.startswith('CADEIA'):
                # Declaração de variáveis
                self.tratar_declaracao(linha)
            elif linha.startswith('PRINT'):
                # Comando de impressão
                self.tratar_print(linha)
            else:
                # Atribuição de valor
                self.tratar_atribuicao(linha)

    def tratar_declaracao(self, linha):
        # Trata declarações de variáveis
        tipo, restante = linha.split(' ', 1)
        declaracoes = [x.strip() for x in restante.split(',')]
        for decl in declaracoes:
            if '=' in decl:
                lexema, valor = decl.split('=')
                lexema = lexema.strip()
                valor = valor.strip()
            else:
                lexema = decl.strip()
                valor = "0" if tipo == "NUMERO" else '""' if tipo == "CADEIA" else None
            self.escopo_atual.adicionar_simbolo('variável', lexema, tipo.lower(), valor)

    def tratar_atribuicao(self, linha):
        # Trata atribuições de valores a variáveis
        if '=' in linha:
            lexema, valor = linha.split('=')
            lexema = lexema.strip()
            valor = valor.strip()

            # Verifica se a variável à esquerda está declarada
            var_esquerda = None
            for escopo in reversed(self.pilha_escopos):
                if lexema in escopo:
                    var_esquerda = escopo.obter_simbolo(lexema)
                    break
            if not var_esquerda:
                self.saida.append(f"Erro linha {self.linha_atual}, variável não declarada")
                return

            # Verifica se a variável ou constante à direita está declarada
            var_direita = None
            if re.match(r'^[a-z_][a-z0-9_]*$', valor):
                for escopo in reversed(self.pilha_escopos):
                    if valor in escopo:
                        var_direita = escopo.obter_simbolo(valor)
                        valor = var_direita['valor']
                        break
                if not var_direita:
                    self.saida.append(f"Erro linha {self.linha_atual}, variável não declarada")
                    return
                if var_esquerda['tipo'] != var_direita['tipo']:
                    self.saida.append(f"Erro linha {self.linha_atual}, tipos não compatíveis")
                    return
            else:
                if var_esquerda['tipo'] == 'numero' and not re.match(r'^[+-]?\d+(\.\d+)?$', valor):
                    self.saida.append(f"Erro linha {self.linha_atual}, tipos não compatíveis")
                    return
                elif var_esquerda['tipo'] == 'cadeia' and not re.match(r'^".*"$', valor):
                    self.saida.append(f"Erro linha {self.linha_atual}, tipos não compatíveis")
                    return

            # Atualiza o valor da variável à esquerda
            for escopo in reversed(self.pilha_escopos):
                if lexema in escopo:
                    escopo.atualizar_simbolo(lexema, valor)
                    break

    def tratar_print(self, linha):
        # Trata o comando de impressão
        _, lexema = linha.split(' ')
        lexema = lexema.strip()
        for escopo in reversed(self.pilha_escopos):
            if lexema in escopo:
                valor = escopo.obter_simbolo(lexema)['valor']
                self.saida.append(f"{valor}")
                break
        else:
            self.saida.append(f"Erro linha {self.linha_atual}, variável não declarada")

    def obter_saida(self):
        # Retorna a saída do analisador
        return "\n".join(self.saida)


# Leitura do arquivo e inicialização do analisador
with open("hello.cic", "r") as arquivo:
    entrada = arquivo.readlines()

analisador = AnalisadorSemantico(entrada)
analisador.analisar()

print(analisador.obter_saida())