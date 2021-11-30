# <span style="color:silver">⚿</span> bottomless 

Library for seamless Redis database management
This is the original version. It is not so fast and fancy as [bottomless_ReJSON](https://github.com/mentalblood/bottomless_ReJSON), but more clean and elegant

<br/>

* ⛓️ Based on pass-through keys yet atomic
* 💤 No excess data reading/rewriting
* 👁️ One-class interface
* 🪄 A lot of sugar

<br/>

## 💿 Installation

```bash
python -m pip install bottomless
```

<br/>

## ✒️ Usage

Here are just a few examples

Feel free to use the tests as a manual

### Preparations

```python
from bottomless import RedisInterface

db = RedisInterface("redis://localhost:6379") # just like redis.from_url
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
    # e is a RedisInterface instance, 
    # so to get data you need to call it:
    assert e() == l[i]
    assert e() == db[i]
    i += 1

assert list(db) == [1, 2, 3]
```

<br/>

## 🔬 Testing

```bash
git clone https://github.com/MentalBlood/bottomless
cd bottomless
pytest tests
```

<br/>

## 📈 Benchmarking

Currently benchmarks are organized as tests and have been used for performance enhancements (algorithmic optimizations, requests number decreasing)

```bash
git clone https://github.com/MentalBlood/bottomless
cd bottomless
pytest benchmarks
```

