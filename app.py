import streamlit as st
import json
from datetime import date

st.set_page_config(page_title="AI Study Planner", page_icon="📚", layout="centered")

st.title("📚 AI Study Planner")
st.caption("Enter your weekly hours + topic stats. Get a high-utility weekly plan.")

# ---------- Load preset topics ----------
DEFAULT_TOPICS = [
  {"name":"RSA & Public Key Crypto","frequency":9,"weight":8,"difficulty":7,"confidence":3},
  {"name":"Hashing (SHA)","frequency":7,"weight":6,"difficulty":4,"confidence":5},
  {"name":"Digital Signatures","frequency":8,"weight":7,"difficulty":6,"confidence":4},
  {"name":"TLS Basics","frequency":6,"weight":7,"difficulty":6,"confidence":2},
  {"name":"Kerberos","frequency":5,"weight":6,"difficulty":7,"confidence":2},
  {"name":"IPSec","frequency":6,"weight":6,"difficulty":6,"confidence":3}
]

def score_topic(t):
    weakness = 11 - t["confidence"]     # 1..10 => 10..1
    return (t["frequency"] * t["weight"] * weakness) / max(1, t["difficulty"])

def allocate_hours(total_hours, topics, bucket_ratio):
    # returns dict {topic_name: hours} for a bucket
    scores = [score_topic(t) for t in topics]
    total_score = sum(scores) if sum(scores) > 0 else 1
    bucket_hours = total_hours * bucket_ratio
    alloc = {}
    for t, s in zip(topics, scores):
        alloc[t["name"]] = round(bucket_hours * (s / total_score), 2)
    return alloc

def plan_text(weekly_hours, topics):
    # Buckets: Learn/Practice/Review
    learn = allocate_hours(weekly_hours, topics, 0.50)
    practice = allocate_hours(weekly_hours, topics, 0.35)
    review = allocate_hours(weekly_hours, topics, 0.15)

    ranked = sorted(topics, key=score_topic, reverse=True)

    lines = []
    lines.append(f"Weekly hours: {weekly_hours}")
    lines.append("")
    lines.append("Top priorities (highest utility):")
    for i, t in enumerate(ranked[:5], 1):
        lines.append(f"{i}. {t['name']}  (score: {score_topic(t):.2f})")

    lines.append("\nWeekly allocation:")
    lines.append("\nLEARN (50%)")
    for k, v in sorted(learn.items(), key=lambda x: x[1], reverse=True):
        if v > 0:
            lines.append(f"- {k}: {v}h")

    lines.append("\nPRACTICE (35%)")
    for k, v in sorted(practice.items(), key=lambda x: x[1], reverse=True):
        if v > 0:
            lines.append(f"- {k}: {v}h")

    lines.append("\nREVIEW (15%)")
    for k, v in sorted(review.items(), key=lambda x: x[1], reverse=True):
        if v > 0:
            lines.append(f"- {k}: {v}h")

    lines.append("\nSimple schedule suggestion:")
    lines.append("- 3 days: Learn + quick review")
    lines.append("- 2 days: Practice past questions + error log")
    lines.append("- 1 day: Mixed review + mini mock")
    lines.append("- 1 rest/catch-up day")
    return "\n".join(lines)

# ---------- Inputs ----------
weekly_hours = st.slider("How many hours can you study per week?", 1, 40, 8)
exam_date = st.date_input("Exam date (optional)", value=date.today())

st.subheader("Topics")
st.write("Edit the topic stats. Lower confidence = you’re weaker on it.")

topics = []
for i, t in enumerate(DEFAULT_TOPICS):
    with st.expander(t["name"], expanded=(i < 2)):
        name = st.text_input("Topic name", value=t["name"], key=f"name{i}")
        frequency = st.slider("Frequency in exams (1–10)", 1, 10, t["frequency"], key=f"freq{i}")
        weight = st.slider("Marks/weight (1–10)", 1, 10, t["weight"], key=f"weight{i}")
        difficulty = st.slider("Difficulty (1–10)", 1, 10, t["difficulty"], key=f"diff{i}")
        confidence = st.slider("Your confidence (1–10)", 1, 10, t["confidence"], key=f"conf{i}")

        topics.append({
            "name": name,
            "frequency": frequency,
            "weight": weight,
            "difficulty": difficulty,
            "confidence": confidence
        })

if st.button("Generate Plan ✅"):
    ranked = sorted(topics, key=score_topic, reverse=True)

    st.subheader("Priority Ranking")
    for i, t in enumerate(ranked, 1):
        st.write(f"**{i}. {t['name']}** — score: `{score_topic(t):.2f}`")

    st.subheader("Weekly Plan")
    out = plan_text(weekly_hours, topics)
    st.text_area("Plan output (copy/paste)", out, height=320)

    st.download_button("Download plan as .txt", out, file_name="study_plan.txt")

