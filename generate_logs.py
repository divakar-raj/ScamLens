"""generate_logs.py - creates synthetic sample_logs.csv with planted attacks.
Run: python generate_logs.py   (all data is fake; IPs use documentation ranges)
"""
import random
from datetime import datetime, timedelta
import pandas as pd


def generate(path="sample_logs.csv", seed=7):
    random.seed(seed)
    rows = []
    base = datetime(2026, 10, 22, 9, 0, 0)
    ips = [f"192.168.1.{i}" for i in range(10, 30)]
    user_of = {ip: f"user{i}" for i, ip in enumerate(ips)}
    pages = ["/", "/login", "/home", "/courses", "/notes", "/profile", "/contact"]

    def add(ts, ip, event, user="", url="", status=""):
        rows.append({"timestamp": ts, "ip": ip, "user": user, "event": event, "url": url, "status": status})

    for _ in range(600):
        ts = base + timedelta(seconds=random.randint(0, 8 * 3600))
        ip = random.choice(ips)
        r = random.random()
        if r < 0.80:
            add(ts, ip, "http_request", user_of[ip], random.choice(pages), 200)
        elif r < 0.95:
            add(ts, ip, "login_success", user_of[ip])
        else:
            add(ts, ip, "login_failed", user_of[ip])

    t = base + timedelta(hours=2, minutes=20)
    for k in range(12):
        add(t + timedelta(seconds=k * 14), "203.0.113.45", "login_failed", "admin")
    add(t + timedelta(seconds=190), "203.0.113.45", "login_success", "admin")

    t = base + timedelta(hours=4)
    for k, u in enumerate(["/search?q=' OR 1=1 --", "/item?id=1 UNION SELECT username,password FROM users",
                           "/search?q=%27%20OR%20%271%27%3D%271", "/comment?text=<script>alert(1)</script>"]):
        add(t + timedelta(seconds=k * 20), "198.51.100.23", "http_request", "", u, 200)

    t = base + timedelta(hours=5)
    for k in range(25):
        add(t + timedelta(seconds=k * 2), "198.51.100.77", "http_request", "", f"/admin-{k}", 404)

    add(datetime(2026, 10, 22, 2, 47, 0), "192.168.1.15", "login_success", user_of["192.168.1.15"])

    df = pd.DataFrame(rows).sort_values("timestamp")
    df.to_csv(path, index=False)
    return df


if __name__ == "__main__":
    print(len(generate()), "rows written to sample_logs.csv")
