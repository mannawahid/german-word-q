import streamlit as st
import pandas as pd
import random

# === Page Config ===
st.set_page_config(page_title="Deutsch Wörter Lernen", page_icon="🇩🇪", layout="centered")

st.title("🇩🇪 Deutsch ↔ বাংলা Vocabulary Trainer (Multiple Choice)")
st.caption("Learn German words with Bangla meanings and example sentences. Each page has 20 questions.")

# === Load Excel File ===
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("Meine_Woerter_im_Kurs_Bangla.xlsx")
        df = df.dropna(subset=["German", "Bangla"])
        return df
    except Exception as e:
        st.error(f"⚠️ Error loading file: {e}")
        return pd.DataFrame(columns=["German", "Bangla", "Sentence"])

df = load_data()

if df.empty:
    st.warning("No data found. Please ensure 'Meine_Woerter_im_Kurs_Bangla.xlsx' is uploaded with columns: German | Bangla | Sentence.")
    st.stop()

st.success(f"Loaded {len(df)} words from Excel file ✅")

# === Pagination ===
QUESTIONS_PER_PAGE = 20
total_pages = (len(df) + QUESTIONS_PER_PAGE - 1) // QUESTIONS_PER_PAGE

# Shuffle words
df = df.sample(frac=1, random_state=random.randint(1, 9999)).reset_index(drop=True)

# Select quiz page
page = st.number_input("📄 Select Quiz Page:", 1, total_pages, 1)
start = (page - 1) * QUESTIONS_PER_PAGE
end = start + QUESTIONS_PER_PAGE
quiz_df = df.iloc[start:end]

st.divider()
st.subheader(f"🎯 Multiple Choice Quiz — Page {page} of {total_pages}")

# === Quiz ===
answers = {}
for idx, row in quiz_df.iterrows():
    german_word = row["German"]
    correct_ans = row["Bangla"]
    sentence = str(row.get("Sentence", ""))

    # generate 3 wrong options
    all_bangla = df["Bangla"].tolist()
    wrong_opts = random.sample([b for b in all_bangla if b != correct_ans], k=3) if len(all_bangla) > 3 else []
    options = [correct_ans] + wrong_opts
    random.shuffle(options)

    st.markdown(f"**{idx+1}. What is the Bangla meaning of '{german_word}'?**")
    if sentence and sentence.lower() != "nan":
        st.caption(f"💬 _Example:_ {sentence}")

    selected = st.radio(
        label="Select your answer:",
        options=options,
        key=f"q_{idx}",
        index=None
    )
    answers[german_word] = (selected, correct_ans)

st.divider()

# === Submit ===
if st.button("✅ Submit Quiz"):
    correct = 0
    for word, (chosen, actual) in answers.items():
        if chosen == actual:
            correct += 1

    score = correct / len(answers)
    st.success(f"🎉 You got {correct} out of {len(answers)} correct!")
    st.progress(score)
    st.balloons()

    # Show review table
    review = []
    for word, (chosen, actual) in answers.items():
        review.append({
            "German": word,
            "Your Answer": chosen if chosen else "❌ Not answered",
            "Correct Answer": actual,
            "✅ Correct?": "✔️" if chosen == actual else "❌"
        })
    st.dataframe(pd.DataFrame(review))
