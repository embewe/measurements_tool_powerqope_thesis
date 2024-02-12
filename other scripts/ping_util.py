import json
from ping3 import ping

def ping_resolver(resolver_ip, count=10):
    # Send "count" pings
    delays = []
    for i in range(count):
        try:
            d = ping(resolver_ip, unit='ms')
            if d:
                delays.append(d)
        except Exception as e:
            print('ping error:', e)
            return []
    return delays


if __name__ == "__main__":
    delays = ping_resolver('208.67.222.123')
    print(delays)
