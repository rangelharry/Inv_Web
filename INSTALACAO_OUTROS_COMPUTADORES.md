# 🖥️ GUIA DE INSTALAÇÃO EM OUTROS COMPUTADORES

## 📋 PRÉ-REQUISITOS

### 1. Sistema Operacional
- ✅ Windows 10/11 (recomendado)
- ✅ macOS 10.14+
- ✅ Linux Ubuntu 18.04+

### 2. Python
- **Versão:** Python 3.8 ou superior
- **Download:** https://python.org/downloads/
- **IMPORTANTE:** Marcar "Add Python to PATH" durante instalação no Windows

### 3. Espaço em Disco
- **Mínimo:** 500 MB livres
- **Recomendado:** 1 GB livres (para cache de dependências)

### 4. Conexão com Internet
- Necessária apenas durante a instalação inicial
- Aproximadamente 200 MB de download

---

## 🚀 INSTALAÇÃO AUTOMÁTICA (RECOMENDADA)

### Windows
1. **Baixar arquivos do sistema**
   - Copie toda a pasta `Inv_Web` para o computador destino
   - OU baixe de: [repositório do projeto]

2. **Executar instalação**
   ```cmd
   # Navegar até a pasta
   cd caminho\para\Inv_Web
   
   # Executar instalador
   instalar_web.bat
   ```

3. **Seguir instruções na tela**
   - O instalador verificará Python automaticamente
   - Instalará dependências necessárias
   - Criará ambiente virtual isolado
   - Testará a instalação

### macOS/Linux
```bash
# Navegar até a pasta
cd /caminho/para/Inv_Web

# Dar permissão de execução
chmod +x instalar_web.sh

# Executar instalação
./instalar_web.sh
```

---

## 🛠️ INSTALAÇÃO MANUAL

### 1. Verificar Python
```cmd
python --version
pip --version
```

### 2. Criar ambiente virtual
```cmd
cd Inv_Web
python -m venv venv_web
```

### 3. Ativar ambiente virtual
**Windows:**
```cmd
venv_web\Scripts\activate
```

**macOS/Linux:**
```bash
source venv_web/bin/activate
```

### 4. Instalar dependências
```cmd
# Instalação mínima (mais rápida)
pip install -r requirements_minimal.txt

# OU instalação completa
pip install -r requirements.txt
```

### 5. Testar instalação
```cmd
python -c "import streamlit; print('OK')"
streamlit hello
```

---

## 🎯 EXECUTAR O SISTEMA

### Execução Simples
```cmd
# Windows
executar_web.bat

# macOS/Linux
./executar_web.sh
```

### Execução Manual
```cmd
# Ativar ambiente
venv_web\Scripts\activate   # Windows
source venv_web/bin/activate  # macOS/Linux

# Iniciar sistema
streamlit run app.py
```

### Acesso ao Sistema
- **URL Local:** http://localhost:8501
- **URL Rede:** http://IP_DO_COMPUTADOR:8501

---

## 🔧 SOLUÇÃO DE PROBLEMAS

### Erro: "Python não encontrado"
1. Instalar Python: https://python.org/downloads/
2. Adicionar ao PATH do sistema
3. Reiniciar terminal/prompt

### Erro: "pip não encontrado"
```cmd
python -m ensurepip --upgrade
python -m pip install --upgrade pip
```

### Erro: "Permissão negada"
- **Windows:** Executar como Administrador
- **macOS/Linux:** Usar `sudo` se necessário

### Erro de dependências
```cmd
# Limpar cache pip
pip cache purge

# Reinstalar dependências
pip install -r requirements_minimal.txt --force-reinstall
```

### Erro de porta ocupada
```cmd
# Usar porta alternativa
streamlit run app.py --server.port 8502
```

---

## 🌐 ACESSO REMOTO

### Configurar Firewall (Windows)
1. Painel de Controle → Sistema e Segurança → Windows Defender Firewall
2. Configurações Avançadas → Regras de Entrada → Nova Regra
3. Porta → TCP → 8501 → Permitir

### Descobrir IP do computador
```cmd
# Windows
ipconfig

# macOS/Linux
ifconfig
```

### Executar para rede local
```cmd
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

---

## 📊 RECURSOS DO SISTEMA

### Login Padrão
- **Usuário:** admin
- **Senha:** 123456

### Funcionalidades
- ✅ Controle de Inventário
- ✅ Equipamentos Elétricos
- ✅ Equipamentos Manuais  
- ✅ Controle de Insumos
- ✅ Movimentações
- ✅ Relatórios Completos
- ✅ Dashboard Interativo

---

## 🆘 SUPORTE

### Logs do Sistema
- **Localização:** `logs/sistema.log`
- **Visualizar:** Menu → Configurações → Logs do Sistema

### Backup do Banco
- **Automático:** A cada operação crítica
- **Manual:** Menu → Configurações → Backup

### Contato
- **Email:** [seu-email@exemplo.com]
- **GitHub:** [link-do-repositorio]

---

## 📈 PRÓXIMOS PASSOS

### Personalização
1. Editar `utils/global_css.py` para alterar aparência
2. Modificar `pages/` para adicionar funcionalidades
3. Ajustar `database/connection.py` para outros bancos

### Deploy Online
1. Streamlit Cloud (gratuito): https://share.streamlit.io/
2. Heroku: Seguir `GUIA_DEPLOY_HEROKU.md`
3. Railway: Seguir `GUIA_DEPLOY_RAILWAY.md`

### Atualizações
- Baixar nova versão dos arquivos
- Executar `instalar_web.bat` novamente
- Backup automático preservará dados