import streamlit as st

st.set_page_config(page_title="Bearing Dataset Analysis", layout="wide", initial_sidebar_state="collapsed")
st.title("🔍 Bearing Analysis")
st.divider()

# Define grouped questions with descriptions and links
question_groups = {
  "🟦 Bearing Type vs Performance": [
    {
      "q": "Q1. If we keep the bearing type the same, how does its performance vary across different asset types? If we fix the asset type, how do different bearing types perform?",
      "page": "pages/Q1.py",
      "desc": "Compare bearing performance across various industries, machines, and RPMs."
    },
    {
      "q": "Q2. Within a fixed industry, how do the same bearing types perform across different asset types?",
      "page": "pages/Q2.py",
      "desc": "Helps identify asset-specific suitability of bearings within a single industry."
    },
    {
      "q": "Q3. For the same asset and RPM, which bearing types perform better?",
      "page": "pages/Q3.py",
      "desc": "Find top and bottom performers under identical working conditions."
    },
    {
      "q": "Q4. Do certain bearing types consistently fail earlier than others across different RPM ranges?",
      "page": "pages/Q4.py",
      "desc": "Identify early-failing bearings under low, medium, and high RPM conditions."
    }
  ],
  "🟧 Lubrication & Failure Timing": [
    {
      "q": "Q5. Does lubrication method impact bearing life?",
      "page": "pages/Q5.py",
      "desc": "Evaluate the effect of grease vs oil on bearing lifespan."
    },
    {
      "q": "Q6. How soon after lubrication do bearings fail?",
      "page": "pages/Q6.py",
      "desc": "Understand if failure timing is linked to lubrication intervention."
    },
    {
      "q": "Q7. Is there any association between missing lubrication data and higher severity failures?",
      "page": "pages/Q7.py",
      "desc": "Investigate if 'Not Available' lubrication records correlate with increased risk."
    },
    {
      "q": "Q8. How does lubrication method vary across industries and machine types?",
      "page": "pages/Q8.py",
      "desc": "Reveal industry-specific lubrication practices and their implications."
    }
  ],
  "🟩 Severity & Risk Analysis": [
    {
      "q": "Q9. Does failure severity (Severity Class) correlate with RPM, machine type, or bearing type?",
      "page": "pages/Q9.py",
      "desc": "Discover conditions associated with high-severity failures."
    },
    {
      "q": "Q10. Which RPM ranges result in higher failure severity?",
      "page": "pages/Q10.py",
      "desc": "Explore if low or high RPMs are more prone to severe faults."
    },
    {
      "q": "Q11. Are certain bearing makes associated with consistently higher or lower severity failures?",
      "page": "pages/Q11.py",
      "desc": "Link brand reliability with severity trends to guide procurement decisions."
    }
  ],
  "🟨 Predictive Insights & Preventive Planning": [
    {
      "q": "Q12. What is the ideal preventive replacement interval (median / 75th percentile)?",
      "page": "pages/Q12.py",
      "desc": "Estimate data-driven preventive maintenance thresholds."
    },
    {
      "q": "Q13. What is the median time-to-failure from subscription start across different machine types?",
      "page": "pages/Q13.py",
      "desc": "Assess asset lifespan to schedule preventive replacements accurately."
    },
    {
      "q": "Q14. Can we predict bearing failure severity based on machine type and RPM range?",
      "page": "pages/Q14.py",
      "desc": "Train a simple classifier to estimate severity level before failure occurs."
    }
  ],
  "🟪 Distribution & Design Insights": [
    {
      "q": "Q15. What is the distribution of failures by RPM and machine type?",
      "page": "pages/Q15.py",
      "desc": "Visualize where failure density is highest."
    },
    {
      "q": "Q16. How does bearing make influence lifespan in identical operating conditions?",
      "page": "pages/Q16.py",
      "desc": "Compare bearing brands under the same workloads and speeds."
    },
    {
      "q": "Q17. What is the failure distribution by bearing type and machine type combinations?",
      "page": "pages/Q17.py",
      "desc": "Detect which bearing-machine pairs are most prone to issues."
    },
    {
      "q": "Q18. Do certain industries experience more frequent high-RPM failures than others?",
      "page": "pages/Q18.py",
      "desc": "Explore operational stress by comparing RPM and failure frequency by sector."
    }
  ]
}


# Render all question groups with their cards
for group_title, questions in question_groups.items():
    st.subheader(group_title)
    cols = st.columns(3)
    for i, item in enumerate(questions):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{item['q']}**")
                st.markdown(f"*{item['desc']}*")
                if item["page"]:
                    st.page_link(item["page"], label="View Insights")
                else:
                    st.button(" Coming Soon", key=f"{item['q']}_disabled", disabled=True)

st.divider()
