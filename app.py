import streamlit as st
import google.generativeai as genai
import pandas as pd
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

RESULTS_FILE = "results.csv"
BIAS_WORDS = ["he", "she", "him", "her", "man", "woman", "male", "female", "boy", "girl", "his", "hers"]


def detect_bias(response_text):
    text = response_text.lower()
    count = sum(text.count(word) for word in BIAS_WORDS)
    total_words = max(len(text.split()), 1)
    score = round(count / total_words, 2)
    label = "Possible Gender Bias" if score > 0.05 else "No obvious gender bias detected"
    return label, score


def run_prompt(prompt, model_name, temperature):
    model = genai.GenerativeModel(model_name)
    for attempt in range(3):
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=temperature),
            )
            return response.text
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                st.info("Too many requests. Waiting 20 seconds, then trying again...")
                time.sleep(20)
            else:
                raise e


def save_result(prompt, response_text, model_name, temperature, bias_label, bias_score):
    row = {
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "response": response_text,
        "model": model_name,
        "temperature": temperature,
        "detected_bias": bias_label,
        "bias_score": bias_score,
    }
    df_new = pd.DataFrame([row])
    if os.path.exists(RESULTS_FILE):
        df_new.to_csv(RESULTS_FILE, mode="a", header=False, index=False)
    else:
        df_new.to_csv(RESULTS_FILE, mode="w", header=True, index=False)


st.set_page_config(page_title="Prompt Engineering Lab", layout="centered")
st.title("🧪 Prompt Engineering Laboratory")
st.write("Test the same question with different prompts and check for bias.")

prompt = st.text_area("Prompt", height=150, placeholder="Type your prompt here...")

col1, col2 = st.columns(2)
with col1:
    model_choice = st.selectbox("Model", [
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash",
        "gemini-3.6-flash",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "Other (type below)",
    ])
    custom_model = st.text_input("Custom model name (only if you chose Other)")
    model_name = custom_model.strip() if model_choice == "Other (type below)" else model_choice
with col2:
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)

if st.button("Run Experiment"):
    if not prompt.strip():
        st.warning("Please type a prompt first.")
    elif not model_name:
        st.warning("Please type a model name.")
    else:
        with st.spinner("Running..."):
            try:
                response_text = run_prompt(prompt, model_name, temperature)
                bias_label, bias_score = detect_bias(response_text)
                save_result(prompt, response_text, model_name, temperature, bias_label, bias_score)
                st.subheader("Model Response")
                st.write(response_text)
                st.subheader("Possible Bias")
                st.write(bias_label)
                st.subheader("Score")
                st.write(bias_score)
            except Exception as e:
                st.error(f"Something went wrong: {e}")

st.divider()
st.subheader("All Past Results")
if os.path.exists(RESULTS_FILE):
    df = pd.read_csv(RESULTS_FILE)
    st.dataframe(df)
    st.download_button("Download JSON", df.to_json(orient="records", indent=2), file_name="results.json")
else:
    st.info("No results yet. Run an experiment above.")