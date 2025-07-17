# Code Citations

## License: unknown
https://github.com/newrelic/docs-website/tree/cb8392984e9a0f6ba6e56cdc03e897c6e82a5c29/src/install/python/python-agent-uvicorn-docker.mdx

```
no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
``
```


## License: unknown
https://github.com/angelika233/FastAPI_PostgreSQL/tree/9318b2325d6a9309c278a1471a12238facff4e93/Dockerfile.fastapi

```
slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0
```


## License: unknown
https://github.com/pedro-canedo/API_STORE/tree/c659833619836a21dbcb033101c3ed3b8ababc98/Dockerfile

```
app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "
```

