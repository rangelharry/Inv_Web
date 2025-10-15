# 📋 Manual do Usuário - Sistema de Inventário Web

## Índice

1. [Introdução](#introdução)
2. [Primeiros Passos](#primeiros-passos)
3. [Interface Principal](#interface-principal)
4. [Módulos do Sistema](#módulos-do-sistema)
5. [Operações Comuns](#operações-comuns)
6. [Relatórios e Exportação](#relatórios-e-exportação)
7. [Configurações](#configurações)
8. [Solução de Problemas](#solução-de-problemas)

## Introdução

O Sistema de Inventário Web é uma solução completa para gestão de equipamentos, insumos e movimentações. Este manual irá guiá-lo através de todas as funcionalidades disponíveis.

### Objetivos do Sistema

- **Controle Total**: Gerencie equipamentos elétricos, manuais e insumos
- **Rastreabilidade**: Histórico completo de movimentações
- **Alertas Inteligentes**: Notificações automáticas para situações importantes
- **Relatórios Avançados**: Análises detalhadas com gráficos e exportação

## Primeiros Passos

### 1. Acesso ao Sistema

1. Abra seu navegador web
2. Acesse `http://localhost:8501` (ou endereço configurado)
3. Faça login com suas credenciais

**Primeiro Acesso (Administrador):**
- Usuário: `admin`
- Senha: `admin123`
- ⚠️ **IMPORTANTE**: Altere a senha no primeiro acesso!

### 2. Tela de Login

![Login](images/login.png)

A tela de login possui:
- Campo de usuário
- Campo de senha
- Botão "Entrar"
- Link "Esqueci minha senha" (futuro)

### 3. Primeiro Login

Após o primeiro login como administrador:

1. **Altere sua senha**:
   - Vá para `Configurações > Segurança > Alterar Senha`
   - Digite a senha atual: `admin123`
   - Defina uma nova senha segura

2. **Configure suas preferências**:
   - Acesse `Configurações > Aparência`
   - Escolha seu tema preferido
   - Ajuste configurações de acessibilidade se necessário

## Interface Principal

### Dashboard

![Dashboard](images/dashboard.png)

O Dashboard é sua tela inicial e contém:

#### 📊 Cartões de Métricas
- **Total de Equipamentos**: Soma de todos os equipamentos
- **Equipamentos Disponíveis**: Prontos para uso
- **Equipamentos em Uso**: Atualmente alocados
- **Total de Insumos**: Materiais em estoque

#### 📈 Gráficos
- **Status dos Equipamentos**: Distribuição por status (Pizza)
- **Movimentações por Mês**: Histórico de movimentações (Barras)
- **Itens por Obra**: Distribuição de equipamentos por local

#### 🚨 Painel de Alertas
- Movimentações pendentes
- Itens com baixo estoque
- Equipamentos sem movimentação há muito tempo

### Navegação Lateral

A barra lateral esquerda contém:

- **🏠 Dashboard**: Tela inicial
- **🚨 Alertas**: Central de notificações
- **⚡ Equipamentos Elétricos**: Gestão de equipamentos elétricos
- **🔧 Equipamentos Manuais**: Gestão de equipamentos manuais
- **📦 Insumos**: Controle de materiais e insumos
- **🏗️ Obras/Departamentos**: Gestão de locais
- **📊 Movimentações**: Registro de transferências
- **📈 Relatórios**: Análises e exportações
- **⚙️ Configurações**: Preferências do sistema

### Informações do Usuário

No topo da barra lateral:
- **Nome do usuário** logado
- **Horário de login**
- **Tempo restante da sessão**
- **Status da conexão**

## Módulos do Sistema

### 1. Equipamentos Elétricos

#### Listagem de Equipamentos

![Equipamentos Elétricos](images/equipamentos_eletricos.png)

**Funcionalidades:**
- **Visualização em tabela** com todos os equipamentos
- **Busca e filtros** por código, descrição, marca, etc.
- **Ordenação** por qualquer coluna
- **Ações rápidas**: Editar, Excluir, Ver Detalhes

#### Cadastro de Novo Equipamento

**Campos obrigatórios:**
- **Código**: Identificador único (ex: EQ001)
- **Descrição**: Nome/descrição do equipamento
- **Marca**: Fabricante do equipamento

**Campos opcionais:**
- **Modelo**: Modelo específico
- **Voltagem**: 110V, 220V, Bivolt
- **Potência**: Em Watts (ex: 650W)
- **Obra/Local**: Onde está localizado
- **Status**: Disponível, Em Uso, Manutenção, etc.
- **Observações**: Informações adicionais

**Processo de Cadastro:**
1. Acesse `Equipamentos Elétricos`
2. Clique em "➕ Novo Equipamento"
3. Preencha os campos obrigatórios
4. Complete informações adicionais
5. Clique em "💾 Salvar"

#### Edição de Equipamentos

1. Na listagem, clique no ícone "✏️" na linha do equipamento
2. Modifique os campos desejados
3. Clique em "💾 Atualizar"

**⚠️ Importante:** Alterações ficam registradas no log de auditoria.

### 2. Equipamentos Manuais

Similar aos equipamentos elétricos, mas com campos específicos:

**Campos específicos:**
- **Categoria**: Tipo de ferramenta (ex: Perfuração, Corte, Medição)
- **Material**: Material principal da ferramenta
- **Tamanho**: Dimensões se aplicável

### 3. Insumos

#### Gestão de Materiais

**Campos principais:**
- **Código**: Identificador único
- **Descrição**: Nome do material
- **Unidade**: Un, Kg, L, m², etc.
- **Quantidade em Estoque**: Quantidade atual
- **Estoque Mínimo**: Limite para alerta
- **Valor Unitário**: Preço por unidade
- **Fornecedor**: Empresa fornecedora

#### Controle de Estoque

**Entradas:**
- Compras
- Devoluções
- Ajustes de inventário

**Saídas:**
- Consumo em obras
- Transferências
- Perdas/quebras

### 4. Obras/Departamentos

#### Cadastro de Locais

**Informações básicas:**
- **Nome**: Nome da obra ou departamento
- **Endereço**: Localização física
- **Responsável**: Pessoa responsável
- **Status**: Ativo, Inativo, Concluído
- **Data de Início**: Quando começou
- **Data Prevista**: Previsão de término

### 5. Movimentações

#### Tipos de Movimentação

**Entrada:**
- Compra de equipamento novo
- Devolução de empréstimo
- Retorno de manutenção

**Saída:**
- Empréstimo para obra
- Envio para manutenção
- Venda/descarte

**Transferência:**
- Entre obras/departamentos
- Mudança de localização

#### Registro de Movimentação

1. Acesse `Movimentações`
2. Clique em "➕ Nova Movimentação"
3. Selecione o **tipo de item** (Equipamento Elétrico, Manual, Insumo)
4. Escolha o **item específico**
5. Defina o **tipo de movimentação**
6. Preencha **origem e destino**
7. Adicione **observações** se necessário
8. Clique em "💾 Registrar"

**Campos automáticos:**
- Data/hora da movimentação
- Usuário responsável
- Histórico de alterações

## Operações Comuns

### 1. Buscar Equipamentos

**Busca simples:**
1. Use a caixa de busca no topo da listagem
2. Digite código, descrição ou marca
3. Os resultados são filtrados automaticamente

**Busca avançada:**
1. Use os filtros laterais
2. Combine múltiplos critérios
3. Aplique filtros de data se necessário

### 2. Transferir Equipamento

**Cenário:** Mover furadeira da Obra A para Obra B

1. Vá para `Movimentações`
2. Clique em "➕ Nova Movimentação"
3. Selecione "Equipamento Elétrico"
4. Escolha a furadeira na lista
5. Tipo: "Transferência"
6. Origem: "Obra A"
7. Destino: "Obra B"
8. Observação: "Transferência por necessidade da obra"
9. Registrar movimentação

### 3. Alertas de Estoque Baixo

**Configurar alertas:**
1. Acesse `Insumos`
2. Edite o item desejado
3. Configure "Estoque Mínimo"
4. Sistema alertará automaticamente quando atingir o limite

**Visualizar alertas:**
1. Dashboard mostra alertas ativos
2. Página `Alertas` lista todos os pendentes
3. Notificações aparecem no topo das páginas

### 4. Gerar Relatório

1. Acesse `Relatórios`
2. Escolha o tipo de relatório:
   - **Inventário Completo**: Todos os itens
   - **Por Status**: Filtrado por situação
   - **Por Obra**: Itens de um local específico
   - **Movimentações**: Histórico de transferências
3. Configure filtros de data
4. Escolha formato de exportação
5. Clique em "📊 Gerar Relatório"

## Relatórios e Exportação

### Tipos de Relatório

#### 1. Relatório de Inventário
- Lista completa de equipamentos e insumos
- Status atual de cada item
- Localização e responsável
- Valor total do inventário

#### 2. Relatório de Movimentações
- Histórico de todas as movimentações
- Filtros por período, usuário, obra
- Análise de fluxo de equipamentos

#### 3. Relatório de Status
- Equipamentos por status (Disponível, Em Uso, etc.)
- Gráficos de distribuição
- Análise de utilização

#### 4. Relatório por Obra
- Inventário específico de cada obra
- Equipamentos alocados vs necessários
- Análise de produtividade

### Formatos de Exportação

**Excel (.xlsx):**
- Formatação avançada
- Múltiplas abas
- Gráficos incluídos
- Ideal para análises detalhadas

**CSV (.csv):**
- Formato universal
- Compatível com qualquer sistema
- Ideal para importação em outros sistemas

**JSON (.json):**
- Formato estruturado
- Ideal para integrações
- Contém metadados completos

**PDF (.pdf):**
- Relatório formatado para impressão
- Layout profissional
- Ideal para apresentações

### Como Exportar

1. Gere o relatório desejado
2. Clique em "📤 Exportar"
3. Escolha o formato
4. Aguarde o processamento
5. Download automático do arquivo

## Configurações

### 1. Aparência e Temas

#### Temas Disponíveis

**Padrão:**
- Cores equilibradas
- Boa legibilidade
- Ideal para uso geral

**Escuro:**
- Fundo escuro
- Reduz cansaço visual
- Ideal para uso prolongado

**Profissional:**
- Visual corporativo
- Cores sóbrias
- Ideal para apresentações

**Moderno:**
- Cores vibrantes
- Visual contemporâneo
- Ideal para interface dinâmica

**Alto Contraste:**
- Máxima legibilidade
- Acessibilidade aprimorada
- Ideal para pessoas com deficiência visual

#### Como Alterar Tema

1. Acesse `Configurações > Aparência`
2. Seção "🎨 Personalização Visual"
3. Escolha o tema desejado
4. Clique em "🎨 Aplicar Tema"
5. Tema é aplicado imediatamente

### 2. Configurações de Sistema

#### Performance
- **Cache**: Acelera carregamento de dados
- **Lazy Loading**: Carrega componentes sob demanda
- **Compressão**: Reduz tamanho dos dados

#### Sessão e Segurança
- **Timeout**: Tempo limite de inatividade
- **Rate Limiting**: Proteção contra ataques
- **Log de Auditoria**: Registro de todas as ações

### 3. Backup e Restauração

#### Backup Automático
- Executado diariamente
- Mantém últimos 7 backups
- Compressão automática

#### Backup Manual
1. Acesse `Configurações > Backup`
2. Clique em "💾 Criar Backup Manual"
3. Aguarde conclusão
4. Arquivo salvo em `/backups/`

#### Restauração
1. Vá para lista de backups
2. Clique em "🔄" no backup desejado
3. Confirme a restauração
4. ⚠️ **Reinicie o sistema após restaurar**

## Solução de Problemas

### Problemas Comuns

#### 1. "Erro ao conectar com banco de dados"

**Causa:** Arquivo de banco corrompido ou sem permissão

**Solução:**
1. Verifique se arquivo `database/inventario.db` existe
2. Verifique permissões de leitura/escrita
3. Se corrompido, restaure do backup mais recente

#### 2. "Sessão expirada"

**Causa:** Tempo limite de inatividade atingido

**Solução:**
1. Faça login novamente
2. Para sessões mais longas, vá em `Configurações > Sistema`
3. Aumente o "Timeout da Sessão"

#### 3. Interface lenta

**Causas possíveis:**
- Cache sobrecarregado
- Muitos registros carregados
- Conexão lenta

**Soluções:**
1. Limpe o cache: `Configurações > Aparência > Limpar Cache`
2. Use filtros para reduzir dados carregados
3. Ative "Lazy Loading" nas configurações

#### 4. Erro ao gerar relatório

**Causas:**
- Muitos dados selecionados
- Filtros incorretos
- Falta de permissão

**Soluções:**
1. Reduza o período do relatório
2. Verifique filtros aplicados
3. Entre em contato com administrador

#### 5. Equipamento não aparece na busca

**Verificações:**
1. Código digitado corretamente
2. Equipamento não foi excluído
3. Filtros não estão escondendo o item
4. Cache desatualizado (limpe o cache)

### Códigos de Erro

| Código | Descrição | Solução |
|--------|-----------|---------|
| E001 | Banco de dados não encontrado | Verificar caminho do arquivo |
| E002 | Permissão negada | Verificar permissões de arquivo |
| E003 | Timeout de conexão | Reiniciar aplicação |
| E004 | Código duplicado | Usar código único |
| E005 | Campo obrigatório | Preencher todos os campos necessários |

### Logs do Sistema

**Localização:** `logs/sistema.log`

**Níveis de log:**
- **INFO**: Operações normais
- **WARNING**: Situações de atenção
- **ERROR**: Erros que impedem operações
- **DEBUG**: Informações detalhadas para diagnóstico

### Contato para Suporte

**Problemas técnicos:**
- Email: suporte.tecnico@inventario-web.com
- Telefone: (11) 1234-5678

**Dúvidas de uso:**
- Email: ajuda@inventario-web.com
- Chat: Disponível no sistema (canto inferior direito)

**Documentação adicional:**
- Wiki: https://github.com/rangelharry/Inv_Web/wiki
- Vídeos tutoriais: https://youtube.com/inventario-web

---

## Apêndices

### A. Atalhos de Teclado

| Atalho | Ação |
|--------|------|
| Ctrl + S | Salvar formulário |
| Ctrl + N | Novo registro |
| Ctrl + F | Buscar |
| Ctrl + P | Imprimir/Exportar |
| F5 | Atualizar página |
| Esc | Cancelar operação |

### B. Glossário

**Auditoria**: Registro de todas as ações realizadas no sistema
**Cache**: Armazenamento temporário para acelerar acesso a dados
**Lazy Loading**: Carregamento sob demanda de componentes
**Rate Limiting**: Controle de quantidade de requests por período
**Timeout**: Tempo limite para operações ou sessões

### C. Changelog

**v2.0.0** (Atual)
- Interface totalmente reformulada
- Sistema de temas personalizáveis
- Performance otimizada com cache
- Alertas automáticos
- Relatórios avançados

**v1.5.0**
- Sistema de backup automático
- Controle de permissões
- Auditoria completa

**v1.0.0**
- Versão inicial
- CRUD básico de equipamentos
- Movimentações simples

---

*Este manual foi atualizado em 15/10/2025 para a versão 2.0 do Sistema de Inventário Web.*