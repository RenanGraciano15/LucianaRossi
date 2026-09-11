# Portal de Evidências Pedagógicas

Aplicação Flask para registrar aulas e armazenar evidências pedagógicas em imagens ou PDF.

## Como executar

1. Crie e ative um ambiente virtual:

	```bash
	python -m venv .venv
	source .venv/bin/activate
	```

2. Instale as dependências:

	```bash
	pip install -r requirements.txt
	```

3. Inicie a aplicação:

	```bash
	python app.py
	```

O banco `evidencias.db` e a pasta `uploads/` são criados automaticamente na primeira execução. Acesse `http://127.0.0.1:5000` no navegador.
