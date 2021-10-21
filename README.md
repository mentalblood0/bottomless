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
from redis import Redis
from CRL import RedisInterface

db = Redis.from_url("redis://localhost:6379")

interface = RedisInterface(config['db']['url'])
```

### Dictionary-like interface

```python
interface.clear()
d = {
    '1': {
        '1': {
            '1': 'one.one.one'
        },
        '2': 'one.two'
    },
    '2': 'two'
}
interface |= d
assert interface() == d

interface['2'] = d
assert interface['2']() == d

interface['1']['1'] = 'lalala'
assert interface['1']['1'] == 'lalala'
assert interface['1']['1']['1'] == None
```

### List-like interface

```python
interface.clear()
l = [1, 2, 3]
interface += [1, 2, 3]

i = 0
for e in interface:
    # e is RedisInterface instance, 
    # so to get data you need to call it:
    assert e() == l[i]
    assert e() == interface[i]
    i += 1

assert list(interface) == [1, 2, 3]
```