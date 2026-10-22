"""Tests for log analysis. Run: pytest"""
import pandas as pd
from generate_logs import generate
from log_detector import analyze_logs


def test_planted_attacks_found():
    generate("sample_logs.csv")
    df = pd.read_csv("sample_logs.csv")
    kinds = {(i["type"], i["ip"]) for i in analyze_logs(df)["incidents"]}
    assert ("Brute-force login attack", "203.0.113.45") in kinds
    assert ("SQL injection attempt", "198.51.100.23") in kinds
    assert ("Cross-site scripting (XSS) attempt", "198.51.100.23") in kinds
    assert ("Scanning for hidden pages", "198.51.100.77") in kinds
    assert ("Unusual-hour login", "192.168.1.15") in kinds


def test_normal_traffic_has_no_attacks():
    df = generate("sample_logs.csv")
    normal = df[df.ip.str.startswith("192.168.1.") & ~df.timestamp.astype(str).str.contains(" 02:")]
    kinds = {i["type"] for i in analyze_logs(normal)["incidents"]}
    assert not kinds & {"Brute-force login attack", "SQL injection attempt", "Scanning for hidden pages"}
