# 🏗️ Sistema de Inventário Web v2.0

Sistema completo de gestão de inventário para obras e empresas, desenvolvido em Python com Streamlit.

## 🚀 Instalação Rápida (Nova Máquina)

### Pré-requisitos
- **Windows 10/11**
- **Python 3.11+** ([Download aqui](https://www.python.org/downloads/))
  - ⚠️ **IMPORTANTE**: Marcar "Add Python to PATH" durante a instalação

### Instalação Automática

1. **Baixe o projeto** ou clone o repositório
2. **Execute o instalador** como Administrador:
   ```batch
   instalar_sistema_completo.bat
   ```

3. **Aguarde a instalação** (5-10 minutos)
   - Criação do ambiente virtual
   - Download de todas as dependências
   - Inicialização do banco de dados
   - Criação de dados de exemplo

4. **Inicie o sistema**:
   ```batch
   executar_sistema.bat
   ```

5. **Acesse no navegador**: http://localhost:8501

### Login Padrão
- **Usuário**: `admin`
- **Senha**: *Definida durante a instalação*

---

## 📋 Funcionalidades

### ⚡ **Equipamentos Elétricos**
- Gestão completa de ferramentas elétricas
- Controle de status (Disponível, Em Uso, Manutenção)
- Movimentação rápida com quantidade
- Filtros avançados por categoria e localização

### 🔧 **Equipamentos Manuais**
- Controle de ferramentas manuais
- Gestão de estado (Novo, Usado, Danificado)
- Movimentação rápida integrada
- Controle por responsável

### 📦 **Insumos e Materiais**
- Controle de estoque em tempo real
- Alertas de estoque baixo
- Entrada/saída rápida
- Controle de preços e valores totais

### 🏗️ **Obras/Departamentos**
- Gestão de obras e projetos
- Controle de departamentos internos
- **33 locais pré-cadastrados** organizados por categoria
- Sistema de edição inline
- Controle de cronograma

### 📊 **Movimentações**
- Registro direto sem aprovação
- Controle de quantidade preciso
- Integração com todos os módulos
- Rastreamento em tempo real

### 📈 **Relatórios Completos**
- Relatórios de inventário
- Análise de movimentações
- Relatórios financeiros
- Métricas em tempo real

### 👥 **Gestão de Usuários**
- Sistema de autenticação
- Controle de acesso
- Logs de atividades

---

## 🗂️ Estrutura do Projeto

```
Inv_Web/
│
├── 📁 database/
│   └── inventario.db           # Banco SQLite
│
├── 📁 pages/
│   ├── dashboard.py           # Página inicial
│   ├── equipamentos_eletricos.py    # Gestão equipamentos elétricos
│   ├── equipamentos_manuais.py      # Gestão equipamentos manuais
│   ├── insumos.py             # Gestão de insumos
│   ├── obras.py               # Obras/Departamentos
│   ├── movimentacoes.py       # Sistema de movimentações
│   ├── relatorios.py          # Relatórios completos
│   └── configuracoes.py       # Configurações do sistema
│
├── 📁 utils/
│   └── auth.py                # Sistema de autenticação
│
├── 📁 database/
│   └── connection.py          # Conexão com banco
│
├── 📁 venv_web/               # Ambiente virtual (criado na instalação)
│
├── app.py                     # Aplicação principal
├── requirements.txt           # Dependências Python
├── instalar_sistema_completo.bat    # Instalador automático
└── executar_sistema.bat       # Inicializador do sistema
```

---

## 🛠️ Instalação Manual (Avançado)

### 1. Clonar Repositório
```bash
git clone [URL_DO_REPOSITORIO]
cd Inv_Web
```

### 2. Criar Ambiente Virtual
```batch
python -m venv venv_web
venv_web\Scripts\activate
```

### 3. Instalar Dependências
```batch
pip install -r requirements.txt
```

### 4. Inicializar Banco
```batch
python -c "from database.connection import init_database; init_database()"
```

### 5. Executar Sistema
```batch
streamlit run app.py --server.port 8501
```

---

## 📊 Dados de Exemplo Incluídos

### Equipamentos Elétricos (8 itens)
- Furadeira Elétrica Bosch GSB 13 RE
- Serra Circular Makita 5007MG
- Parafusadeira Dewalt DCD771C2
- Esmerilhadeira Bosch GWS 700
- Máquina de Solda Inversora 200A
- E mais...

### Equipamentos Manuais (5 itens)
- Martelo Stanley FatMax 20oz
- Chave de Fenda Tramontina 1/4 x 6
- Alicate Universal Gedore 8 pol
- Nível de Alumínio Vonder 40cm
- Trena Stanley 5m

### Insumos (5 categorias)
- Parafusos Phillips 3,5x25mm (500 unidades)
- Fita Isolante Preta 19mm (25 peças)
- Cabo Flexível 2,5mm² Azul (100 metros)
- Tinta Acrílica Branca 18L (5 litas)
- Lixa Madeira Grão 120 (50 unidades)

### Obras/Departamentos (5 locais)
- Obra - Residencial Vista Alegre
- Obra - Edifício Comercial Centro
- Obra - Shopping Mall Norte
- Departamento - Almoxarifado Central
- Departamento - Manutenção

---

## 🔧 Configurações Avançadas

### Alterar Porta do Servidor
Edite o arquivo `executar_sistema.bat` e altere:
```batch
streamlit run app.py --server.port 8501
```

### Backup do Banco de Dados
O banco SQLite está em: `database/inventario.db`
Faça cópias regulares deste arquivo.

### Logs do Sistema
Os logs são exibidos no terminal durante a execução.

---

## 🆘 Solução de Problemas

### Erro: "Python não encontrado"
- Instale o Python 3.11+ do site oficial
- Certifique-se de marcar "Add Python to PATH"
- Reinicie o terminal/prompt

### Erro: "pip não encontrado"
```batch
python -m ensurepip --upgrade
python -m pip install --upgrade pip
```

### Erro: "Módulo não encontrado"
```batch
venv_web\Scripts\activate
pip install -r requirements.txt
```

### Sistema não abre no navegador
- Verifique se a porta 8501 está livre
- Acesse manualmente: http://localhost:8501
- Tente uma porta diferente: `--server.port 8502`

### Erro de Banco de Dados
- Exclua o arquivo `database/inventario.db`
- Execute novamente `instalar_sistema_completo.bat`

---

## 📈 Próximos Recursos (Roadmap)

- [ ] 📱 Interface mobile responsiva
- [ ] 📧 Notificações por email
- [ ] 📊 Dashboard com gráficos avançados
- [ ] 🔄 Sincronização em nuvem
- [ ] 📋 Etiquetas com QR Code
- [ ] 🎯 Relatórios personalizáveis
- [ ] 👥 Perfis de usuário com permissões
- [ ] 📅 Agendamento de manutenções

---

## 🤝 Contribuição

1. Fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

---

## 📞 Suporte

- **Email**: suporte@inventario.com
- **Documentação**: [Link para documentação]
- **Issues**: [Link para GitHub Issues]

---

## 🎯 Versão Atual: v2.0

### ✨ Novidades desta versão:
- ✅ Sistema de movimentação rápida
- ✅ Integração completa entre módulos
- ✅ Interface moderna e intuitiva
- ✅ 33 locais pré-cadastrados
- ✅ Instalador automático
- ✅ Banco de dados com exemplos
- ✅ Sistema de edição inline
- ✅ Controle de quantidade preciso
- ✅ Relatórios completos

---

**Desenvolvido com ❤️ usando Python + Streamlit**