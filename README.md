# Traces 5 API

## Dev

```bash
$ mkvirtualenv traces
$ pip install -r requirements.txt
$ python app.py
```

### Database

Requires running PostgreSQL instance.

```bash
$ createdb traces
```

Then in a Python shell:

```python
>>> from app import db
>>> db.create_all()
```

## Testing

```bash
$ curl http://localhost:5000/traces -X POST -d "page=homepage" -d "trace=[[1,5],[6,6],[9,14],[23,77]]"
```
