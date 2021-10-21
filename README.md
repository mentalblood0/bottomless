# 👌 CRL (Correct Redis Library)

Library to easily manage data in Redis databases

Features:

* 😴 No excess data reading/rewriting
* ⚛️ Through-keys yet atomic
* 🧐 One-class interface
* 🍬 A lot of sugar



## 💽 Installation

```bash
python -m pip install CRL
```



## ✍️ Usage

Here are just a few examples

Feel free to use the tests as a manual

### Preparations

```python
from CRL import RedisInterface

db = RedisInterface("redis://localhost:6379")
```

### Dictionary-like interface

```python
db.clear()
d = {
    '1': {
        '1': {
            '1': 'one.one.one'
        },
        '2': 'one.two'
    },
    '2': 'two'
}
db |= d
assert db() == d

db['2'] = d
assert db['2']() == d

db['1']['1'] = 'lalala'
assert db['1']['1'] == 'lalala'
assert db['1']['1']['1'] == None
```

### List-like interface

```python
db.clear()
l = [1, 2, 3]
db += [1, 2, 3]

i = 0
for e in db:
    # e is RedisInterface instance, 
    # so to get data you need to call it:
    assert e() == l[i]
    assert e() == db[i]
    i += 1

assert list(db) == [1, 2, 3]
```