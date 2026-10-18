"""app.py - Streamlit interface. Run with: streamlit run app.py"""
import html
import pandas as pd
import streamlit as st
from detector import analyze
from explainer import explain
from batch import analyze_dataframe
from test_cases import SAMPLES

st.set_page_config(page_title="ScamLens", page_icon="🛡️", layout="wide")
st.title("🛡️ ScamLens")
st.caption("Understand suspicious messages before acting on them.")


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
        out += html.escape(text[pos:s])
        out += f"<mark>{html.escape(text[s:e])}</mark>"
        pos = e
    out += html.escape(text[pos:])
    return out.replace("\n", "<br>")


tab_single, tab_batch = st.tabs(["Single message", "Batch (CSV upload)"])

# ---------- Tab 1: single message ----------
with tab_single:
    sample_name = st.selectbox("Try a sample message (optional)", ["-- none --"] + [s["name"] for s in SAMPLES])
    default_text = ""
    if sample_name != "-- none --":
        default_text = next(s["text"] for s in SAMPLES if s["name"] == sample_name)

    message = st.text_area("Paste a message here", value=default_text, height=160)

    if st.button("Analyze", type="primary"):
        if not message.strip():
            st.warning("Please paste a message first.")
        else:
            result = analyze(message)
            left, right = st.columns([3, 2])

            with left:
                st.subheader("Inspection result")
                st.metric("Risk level", f"{result['level']} ({result['score']}%)")
                st.progress(result["score"] / 100)

                with st.spinner("Writing explanation..."):
                    explanation, source = explain(message, result)
                st.markdown(f"**Why it matters** _(by {source})_")
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
                st.subheader("Do this now")
                st.markdown(
                    "1. **Do not** share any OTP, PIN or password with anyone.\n"
                    "2. **Do not** click links or reply to the message.\n"
                    "3. Contact the organisation using the **official number or website**, not the one in the message.\n"
                    "4. Block the sender.\n"
                    "5. Report scams (India: cybercrime.gov.in or call 1930)."
                )
                st.info(
                    "AI limitations: this tool checks only the text you pasted. "
                    "It cannot confirm who really sent it. Rules can miss new scam styles "
                    "or flag genuine messages."
                )

# ---------- Tab 2: batch CSV ----------
with tab_batch:
    st.write("Upload a CSV with one message per row.")
    uploaded = st.file_uploader("CSV file", type=["csv"])
    if uploaded is not None:
        df = pd.read_csv(uploaded)
        column = st.selectbox("Which column has the text?", df.columns)
        if st.button("Analyze all rows"):
            out = analyze_dataframe(df, column)
            c1, c2, c3 = st.columns(3)
            c1.metric("Rows", len(out))
            c2.metric("High risk", int((out["risk_level"] == "High").sum()))
            c3.metric("Average score", round(out["risk_score"].mean()))
            st.bar_chart(out["risk_level"].value_counts())
            st.dataframe(out, use_container_width=True)
            st.download_button("Download results", out.to_csv(index=False), "results.csv", "text/csv")
