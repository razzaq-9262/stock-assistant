"""Streamlit UI: chat + charts + tables.  Run: streamlit run app.py"""
import streamlit as st

from tools import calculations, fundamental, technical

st.set_page_config(page_title="AI Stock Assistant", layout="wide")
st.title("AI Stock Market Assistant")
st.caption("Educational use only - not financial advice. Data: Yahoo Finance.")

tab_chat, tab_tech, tab_fund, tab_calc = st.tabs(
    ["Chat", "Technical", "Fundamental", "Calculations"])

with tab_chat:
    if "history" not in st.session_state:
        st.session_state.history = []
    for msg in st.session_state.history:
        st.chat_message(msg["role"]).write(msg["content"])
    question = st.chat_input("Ask e.g. 'Is AAPL overbought?' or 'Compare AAPL and MSFT'")
    if question:
        st.chat_message("user").write(question)
        try:
            from harness import ask
            with st.spinner("Analyzing..."):
                answer = ask(question, st.session_state.history)
        except Exception as exc:
            answer = f"Error: {exc} (is ANTHROPIC_API_KEY set?)"
        st.chat_message("assistant").write(answer)
        st.session_state.history += [
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer}]

with tab_tech:
    tk = st.text_input("Ticker", "AAPL", key="tech_tk").upper()
    period = st.selectbox("Period", ["3mo", "6mo", "1y", "2y"], index=1)
    if st.button("Show chart"):
        try:
            df = technical.add_indicators(technical.get_prices(tk, period))
            st.plotly_chart(technical.candlestick_chart(df, tk),
                            use_container_width=True)
            st.json(technical.trend_summary(df))
        except Exception as exc:
            st.error(str(exc))

with tab_fund:
    tk2 = st.text_input("Ticker", "AAPL", key="fund_tk").upper()
    if st.button("Show fundamentals"):
        try:
            data = fundamental.get_fundamentals(tk2)
            st.dataframe(fundamental.fundamentals_table(data).astype(str),
                         use_container_width=True)
        except Exception as exc:
            st.error(str(exc))

with tab_calc:
    st.subheader("Compare stocks")
    raw = st.text_input("Tickers (comma separated)", "AAPL, MSFT, GOOGL")
    if st.button("Compare"):
        tickers = [t.strip().upper() for t in raw.split(",") if t.strip()]
        st.dataframe(calculations.compare_stocks(tickers),
                     use_container_width=True)

    st.subheader("What-if: investment growth")
    c1, c2, c3 = st.columns(3)
    amount = c1.number_input("Amount", value=100000.0)
    rate = c2.number_input("Annual return %", value=8.0)
    years = c3.number_input("Years", value=5, step=1)
    if st.button("Project"):
        proj = calculations.project_value(amount, rate, int(years))
        st.line_chart(proj.set_index("Year"))
        st.dataframe(calculations.scenarios(amount, int(years)))
        st.caption("Assumption: constant return, compounded monthly.")
