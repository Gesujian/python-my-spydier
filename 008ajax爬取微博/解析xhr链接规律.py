from urllib.parse import urlparse
from urllib.parse import parse_qs
with open('微博首页xhr.txt', 'r') as xhr_file:
    items = xhr_file.readlines()
    items = [item.strip() for item in items]

results = []
for item in items:
    result = urlparse(item)
    results.append(result[4])

query = []
for r in results:
    p = parse_qs(r)
    query.append(p)

# min_id   pagebar =2,3,4,5  unread_max_id == unread_since_id    __rnd

for i in query:
    print(i['min_id']," ",i['pagebar']," ",i['unread_max_id']," ",i['__rnd'])