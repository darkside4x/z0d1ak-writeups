from pwn import *
import networkx as nx
import pulp
import re

context.log_level = 'debug'
r = remote('chals2.apoorvctf.xyz', 14001)

r.recvuntil(b'Graph:')
r.recvline()
r.recvline()

raw = r.recvuntil(b'Submit', drop=True).decode('utf-8', 'ignore')
c_raw = re.sub(r'\x1b\[.*?m', '', raw)

e = []
for l in c_raw.split('\n'):
    p = l.strip().split()
    if len(p) == 2 and p[0].isdigit() and p[1].isdigit():
        e.append((int(p[0]), int(p[1])))

g = nx.Graph()
g.add_edges_from(e)

pr = pulp.LpProblem("MVC", pulp.LpMinimize)
x = pulp.LpVariable.dicts("x", list(g.nodes()), cat='Binary')

pr += pulp.lpSum([x[i] for i in g.nodes()])

for u, v in g.edges():
    pr += x[u] + x[v] >= 1

pr.solve(pulp.PULP_CBC_CMD(msg=False))

a = sorted([v for v in g.nodes() if pulp.value(x[v]) == 1.0])
ans = " ".join(map(str, a))

r.sendlineafter(b'answer:', ans.encode())
r.interactive()