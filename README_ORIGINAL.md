# 🌐 Sistema de Inventário Web

## 📋 Visão Geral

Versão web multiusuário do Sistema de Inventário, desenvolvida com **Streamlit** para acesso online gratuito.

### ✨ Características

- 🌐 **Acesso Web**: Interface moderna acessível via navegador
- 👥 **Multiusuário**: Múltiplos usuários simultâneos
- 🔒 **Seguro**: Sistema de login e sessões
- 📱 **Responsivo**: Funciona em desktop, tablet e mobile
- 🆓 **Gratuito**: Hospedagem gratuita no Streamlit Cloud
- ⚡ **Rápido**: Interface reativa em tempo real

---

## 🚀 Instalação Rápida

### 1. Requisitos
- Python 3.8+
- Conexão com internet (para install de dependências)

### 2. Instalação Automática
```bash
# Execute o instalador
instalar_web.bat

# Ou manualmente:
pip install streamlit pandas plotly
streamlit run app.py
```

### 3. Acesso ao Sistema
- **URL Local**: http://localhost:8501
- **Login**: admin / 123456 ou cinthia / C1nt1@2024

---

## 📁 Estrutura do Projeto

```
Inv_Web/
├── app.py                    # Aplicação principal
├── requirements.txt          # Dependências
├── instalar_web.bat         # Instalador automático
├── executar_web.bat         # Executar sistema
├── .streamlit/
│   └── config.toml          # Configurações Streamlit
├── database/
│   ├── connection.py        # Conexão com banco
│   └── inventario.db        # Banco SQLite
├── utils/
│   └── auth.py              # Sistema de autenticação
├── pages/                   # Páginas do sistema
│   ├── dashboard.py         # Dashboard principal
│   ├── equipamentos_eletricos.py
│   ├── equipamentos_manuais.py
│   ├── insumos.py
│   ├── obras.py
│   ├── movimentacoes.py
│   ├── relatorios.py
│   └── configuracoes.py
└── static/                  # Arquivos estáticos
```

---

## 🎯 Funcionalidades

### ✅ Implementadas
- 🔐 **Sistema de Login** - Autenticação segura
- 🏠 **Dashboard** - Métricas e visão geral
- ⚡ **Equipamentos Elétricos** - CRUD completo
- 📊 **Gráficos Interativos** - Plotly charts
- 🔍 **Busca em Tempo Real** - Filtros dinâmicos
- 👤 **Gestão de Sessões** - Controle de usuários

### 🔄 Em Desenvolvimento (70% concluído)
- 🔧 **Equipamentos Manuais** - Interface completa
- 📦 **Insumos** - Controle de estoque
- 🏗️ **Obras** - Gestão de projetos
- 📊 **Movimentações** - Transferências
- 📈 **Relatórios** - Exportação e gráficos
- ⚙️ **Configurações** - Preferências

---

## 👥 Acesso Multiusuário

### Local (Rede Interna)
```bash
# Outros usuários na mesma rede podem acessar via:
http://SEU_IP:8501

# Para descobrir seu IP:
ipconfig
```

### Online (Internet)
```bash
# Deploy gratuito no Streamlit Cloud:
1. Fazer upload para GitHub
2. Conectar com Streamlit Cloud
3. Deploy automático
4. URL: https://seu-app.streamlit.app
```

---

## 🛠️ Desenvolvimento

### Executar em Modo Desenvolvimento
```bash
executar_dev.bat
# ou
streamlit run app.py --server.runOnSave true
```

### Adicionar Nova Página
1. Criar arquivo em `pages/nova_pagina.py`
2. Implementar função `show()`
3. Adicionar no menu em `app.py`

### Personalizar Interface
- **CSS**: Editar estilos em `app.py`
- **Configurações**: Modificar `.streamlit/config.toml`
- **Cores**: Alterar tema nas configurações

---

## 🔒 Segurança

### Sistema de Autenticação
- Senhas criptografadas (SHA256)
- Sessões com timeout
- Log de auditoria
- Controle de acesso por página

### Dados
- Banco SQLite local
- Backup automático
- Transações seguras
- Validação de entrada

---

## 📊 Métricas e Monitoramento

### Dashboard Inclui:
- Total de equipamentos
- Status de disponibilidade
- Alertas de estoque baixo
- Valor do inventário
- Movimentações recentes
- Gráficos interativos

### Relatórios:
- Inventário completo
- Por categoria
- Por localização
- Movimentações por período
- Auditoria de ações

---

## 🆘 Solução de Problemas

### Erro: "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install streamlit
# ou execute: instalar_web.bat
```

### Erro: "Database not found"
```bash
# Copie o banco da versão desktop:
copy "..\inv\inventario.db" "database\inventario.db"
```

### Erro: "Port 8501 already in use"
```bash
# Use porta diferente:
streamlit run app.py --server.port 8502
```

### Sistema lento
```bash
# Verifique quantidade de dados
# Para grandes volumes, considere paginação
```

---

## 🌟 Deploy Online (Gratuito)

### Streamlit Cloud
1. **Criar repositório GitHub**
   ```bash
   git init
   git add .
   git commit -m "Versão web inicial"
   git remote add origin https://github.com/USUARIO/inventario-web.git
   git push -u origin main
   ```

2. **Deploy no Streamlit Cloud**
   - Acesse: https://share.streamlit.io
   - Conecte GitHub
   - Selecione repositório
   - App file: `app.py`
   - Deploy automático!

3. **URL Final**
   ```
   https://USUARIO-inventario-web-app-HASH.streamlit.app
   ```

### Railway (Alternativa)
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

---

## 📈 Roadmap

### Versão 2.1 (Próximas 2 semanas)
- ✅ Completar todas as páginas
- ✅ Sistema de notificações
- ✅ Backup automático
- ✅ Relatórios avançados

### Versão 2.2 (Próximo mês)
- 📱 App mobile (PWA)
- 🔔 Notificações push
- 📧 Relatórios por email
- 🎨 Temas personalizáveis

### Versão 3.0 (Futuro)
- 🤖 IA para previsão de estoque
- 📊 Business Intelligence
- 🔄 Sincronização multi-filial
- 📱 App nativo mobile

---

## 🤝 Contribuição

### Como Contribuir
1. Fork o projeto
2. Crie branch para feature
3. Commit das mudanças
4. Push para branch
5. Abra Pull Request

### Áreas que Precisam de Ajuda
- 🎨 Design/UX
- 📊 Relatórios avançados
- 📱 Responsividade mobile
- 🧪 Testes automatizados
- 📖 Documentação

---

## 📞 Suporte

### Problemas Técnicos
- Criar issue no GitHub
- Incluir: SO, Python version, mensagem de erro
- Print da tela se possível

### Sugestões de Funcionalidades
- Abrir discussão no GitHub
- Descrever caso de uso
- Mockups são bem-vindos

---

## 📄 Licença

Este projeto é de uso interno. Todos os direitos reservados.

---

## 🎉 Créditos

**Desenvolvido com:**
- [Streamlit](https://streamlit.io/) - Framework web
- [Plotly](https://plotly.com/) - Gráficos interativos
- [Pandas](https://pandas.pydata.org/) - Manipulação de dados
- [SQLite](https://sqlite.org/) - Banco de dados

**2025 - Sistema de Inventário Web v2.0**