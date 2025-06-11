# WS-Poked-X-Project

Projeto de Web Semântica com integração entre GraphDB e uma aplicação web para consulta e exploração de dados sobre Pokémon.

---

## Como correr o projeto

### 1. Instalar e correr o GraphDB

```bash
# Transferir e extrair GraphDB
wget https://graphdb.ontotext.com/repositories/graphdb-free/GraphDB-Free-10.8.4-dist.zip
unzip GraphDB-Free-10.8.4-dist.zip
cd GraphDB-Free-10.8.4

# Criar pasta para dados persistentes
mkdir -p ~/graphdb-data

# Iniciar GraphDB com configurações
GRAPHDB_HOME=~/graphdb-data \
GRAPHDB_MIN_DISK_SPACE_MB=50 \
JAVA_OPTS="-Dgraphdb.workbench.maxUploadSize=5000000" \
bash bin/graphdb
```

O GraphDB ficará disponível em: http://localhost:7200

---

No separador Import, escolha Upload RDF Files e carregue os arquivos na seguinte ordem (todos para "The default graph"):

app/database/ontology_new.ttl

app/database/pokemon-data-aligned-new.ttl

app/database/type_effectiveness_data.ttl

### 2. Correr a aplicação web

```bash
# Ir para o diretório do projeto
cd WS-Poked-X-Project

# Ativar ambiente virtual e instalar dependências
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Iniciar o servidor local
python manage.py runserver 8000
```

A aplicação estará disponível em: http://localhost:8000

---

# WS-Poked-X Project Setup Guide

## Pré-requisitos

- Python ≥ 3.10 (recomenda-se 3.12)
- `pip` e `virtualenv` (ou `python -m venv`)
- GraphDB (edição gratuita) instalado localmente
- Git
- Navegador Web recente

---

## Passo 1 — Obter o código-fonte

```bash
git clone https://github.com/ftferreira02/WS-Poked-X-Project.git
cd WS-Poked-X-Project
```

---

## Passo 2 — Criar o ambiente Python

```bash
python -m venv venv          # cria ambiente virtual

# Ativação:
source venv/bin/activate     # Mac/Linux
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

---

## Passo 3 — Configurar e arrancar o GraphDB

1. Inicie o GraphDB (use o script `graphdb` ou `graphdb.bat` conforme seu sistema).
2. Abra `http://localhost:7200` no navegador.
3. Crie um repositório com as seguintes opções:
   - **Nome:** `Poked-X`
   - **Regra de inferência:** `OWL 2 RL`
4. No separador **Import**, escolha **Upload RDF Files** e carregue os arquivos na seguinte ordem **(todos para "The default graph")**:
   - `ontology_new.ttl`
   - `pokemon-data-aligned-new.ttl`
   - `type_effectiveness_data.ttl`
5. Clique **Import** e aguarde o término (barra verde).

---

## Passo 4 — Migrar a BD Django e lançar o servidor

```bash
python manage.py migrate       # aplica migrações locais
python manage.py runserver 8000
```

A aplicação Django estará disponível em:  
 http://localhost:8000/

---

## Passo 5 — Aceder à aplicação

- **Interface Web:** [http://localhost:8000/](http://localhost:8000/)
- **GraphDB Workbench:** [http://localhost:7200/](http://localhost:7200/)

## Estrutura do Projeto Django

```text
WS-POKED-X-Project/
├── manage.py                # Utilitário para interagir com o projeto
├── webproj/                 # Pacote principal do projeto Django
│   ├── __init__.py
│   ├── settings.py          # Configurações do Django
│   ├── urls.py              # Routing das URLs
│   └── wsgi.py              # Entrada para servidores WSGI
├── app/                     # Aplicação principal
│   ├── __init__.py
│   ├── admin.py             # Interface administrativa
│   ├── forms.py             # Formulários para input do utilizador
│   ├── models/              # Modelos de dados
│   │   ├── __init__.py
│   │   ├── fight/
│   │   │   └── fight_model.py
│   │   ├── search/
│   │   │   └── search_model.py
│   │   └── stats/
│   │       └── stats_model.py
│   ├── views/               # Lógica para lidar com pedidos
│   │   ├── __init__.py
│   │   ├── fight/
│   │   │   └── fight_view.py
│   │   ├── search/
│   │   │   └── search_view.py
│   │   └── stats/
│   │       └── stats_view.py
│   ├── templates/           # Ficheiros HTML
│   └── static/              # CSS, JS, imagens, etc.
```