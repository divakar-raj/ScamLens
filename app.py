import html
import os
import pandas as pd
import streamlit as st
from detector import analyze
from explainer import explain, explain_logs
from batch import analyze_dataframe
from log_detector import analyze_logs
from generate_logs import generate
from i18n import NEXT_STEPS, TITLES, UI_LANGS, text_lang
from test_cases import TEST_MESSAGES

st.set_page_config(page_title="ScamLens", page_icon="🛡️", layout="wide")
st.title("🛡️ ScamLens")
st.caption("Understand suspicious messages and security logs, in your own language, before acting on them.")

choice = st.sidebar.selectbox("Explanation language", UI_LANGS)
st.sidebar.caption("Auto = same language as the message.")


def highlight(text: str, findings: list) -> str:
    spans = sorted((e["start"], e["end"]) for f in findings for e in f["evidence"])
    merged = []
    for s, e in spans:
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    out, pos = "", 0
    for s, e in merged:
        out += html.escape(text[pos:s]) + f"<mark>{html.escape(text[s:e])}</mark>"
        pos = e
    out += html.escape(text[pos:])
    return out.replace("\n", "<br>")


tab_msg, tab_batch, tab_logs = st.tabs(["Message check", "Batch (CSV)", "Log analysis"])

with tab_msg:
    sample_name = st.selectbox("Try a sample message (optional)", ["-- none --"] + [s["category"] for s in TEST_MESSAGES])
    default_text = next((s["text"] for s in TEST_MESSAGES if s["category"] == sample_name), "")
    message = st.text_area("Paste a message here", value=default_text, height=160)

    if st.button("Analyze", type="primary"):
        if not message.strip():
            st.warning("Please paste a message first.")
        else:
            result = analyze(message)
            lang = result["language"] if choice == "Auto" else choice
            tl = text_lang(lang)
            left, right = st.columns([3, 2])

            with left:
                st.subheader("Inspection result")
                c1, c2 = st.columns(2)
                c1.metric("Risk level", f"{result['level']} ({result['score']}%)")
                c2.metric("Detected language", result["language"])
                st.progress(result["score"] / 100)

                with st.spinner("Writing explanation..."):
                    explanation, source = explain(message, result, lang)
                st.markdown(f"**{TITLES[tl]['why']}** _(by {source})_")
                st.write(explanation)

                st.subheader("Warning signs found")
                if result["findings"]:
                    st.markdown(highlight(message, result["findings"]), unsafe_allow_html=True)
                    for f in result["findings"]:
                        with st.expander(f"{f['rule']}  (severity {f['severity']}/3)"):
                            st.write(f["why"])
                            st.write("Found: " + ", ".join(f"`{e['text']}`" for e in f["evidence"]))
                else:
                    st.success("No common scam signs found. Stay careful anyway.")

            with right:
                st.subheader(TITLES[tl]["steps"])
                st.markdown("\n".join(f"{i}. {s}" for i, s in enumerate(NEXT_STEPS[tl], 1)))
                st.info("AI limitations: this tool checks only the text you pasted. It cannot confirm who "
                        "really sent it. Rules can miss new scam styles or flag genuine messages.")

with tab_batch:
    st.write("Upload a CSV with one message per row.")
    uploaded = st.file_uploader("Messages CSV", type=["csv"], key="msg_csv")
    if uploaded is not None:
        df = pd.read_csv(uploaded)
        column = st.selectbox("Which column has the text?", df.columns)
        if st.button("Analyze all rows"):
            out = analyze_dataframe(df, column)
            c1, c2, c3 = st.columns(3)
            c1.metric("Rows", len(out))
            c2.metric("High risk", int((out["risk_level"] == "High").sum()))
            c3.metric("Average score", round(out["risk_score"].mean()))
            
            # Added red color to the bar chart for presentation impact
            st.bar_chart(out["risk_level"].value_counts(), color="#ff4b4b")
            
            # Highlight High Risk rows in light red
            def highlight_high_risk(val):
                return 'background-color: #ffcccc; color: #900000' if val == 'High' else ''
                
            st.dataframe(out.style.map(highlight_high_risk, subset=['risk_level']), use_container_width=True)
            
            st.download_button("Download results", out.to_csv(index=False), "results.csv", "text/csv")

with tab_logs:
    st.write("Upload a security log CSV (columns: timestamp, ip, user, event, url, status) "
             "or use the built-in synthetic sample.")
    up = st.file_uploader("Log CSV", type=["csv"], key="log_csv")
    use_sample = st.button("Use sample logs")
    logs = None
    if up is not None:
        logs = pd.read_csv(up)
    elif use_sample or st.session_state.get("sample_logs"):
        st.session_state["sample_logs"] = True
        if not os.path.exists("sample_logs.csv"):
            generate("sample_logs.csv")
        logs = pd.read_csv("sample_logs.csv")

    if logs is not None:
        missing = {"timestamp", "ip", "event"} - set(logs.columns)
        if missing:
            st.error(f"Missing required columns: {', '.join(sorted(missing))}")
        else:
            res = analyze_logs(logs)
            inc = res["incidents"]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Events", res["events"])
            c2.metric("Unique IPs", res["ips"])
            c3.metric("Incidents", len(inc))
            c4.metric("Severity 3", sum(1 for i in inc if i["severity"] == 3))

            if inc:
                table = pd.DataFrame(inc)[["severity", "type", "ip", "count", "first_seen", "evidence"]]
                st.bar_chart(table["type"].value_counts())
                st.dataframe(table, use_container_width=True)

                lang_choice = "English" if choice == "Auto" else choice
                with st.spinner("Writing incident summary..."):
                    summary, source = explain_logs(inc, lang_choice)
                st.markdown(f"**Incident summary** _(by {source})_")
                st.write(summary)

                for i in inc:
                    with st.expander(f"[{i['severity']}/3] {i['type']} from {i['ip']}"):
                        st.write(f"**What we saw:** {i['evidence']}")
                        st.write(f"**Why it matters:** {i['why']}")
                        st.write(f"**What to do:** {i['action']}")
                st.download_button("Download incident report", table.to_csv(index=False),
                                   "incident_report.csv", "text/csv")
            else:
                st.success("No suspicious activity found.")