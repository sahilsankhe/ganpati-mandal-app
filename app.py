import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# -------------------------------------------------------------
# 1. Page Configuration
# -------------------------------------------------------------
st.set_page_config(
    page_title="सार्वजनिक गणेशोत्सव मंडळ, देदाळे",
    page_icon="🪔",
    layout="wide"
)

DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

VARGANI_FILE = os.path.join(DATA_DIR, "vargani.xlsx")
EXPENSE_FILE = os.path.join(DATA_DIR, "expenses.xlsx")
ANNOUNCEMENT_FILE = os.path.join(DATA_DIR, "announcements.xlsx")

def load_data(file_path, columns):
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path)
            for col in columns:
                if col not in df.columns:
                    df[col] = ""
            return df[columns]
        except Exception:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

def save_data(df, file_path):
    df.to_excel(file_path, index=False)

# Excel Data Loading
df_vargani = load_data(VARGANI_FILE, ["Receipt_ID", "Date", "Name", "Address", "Phone", "Amount", "Mode"])
df_expense = load_data(EXPENSE_FILE, ["Expense_ID", "Date", "Category", "Amount"])
df_announcement = load_data(ANNOUNCEMENT_FILE, ["ID", "Date", "Announcement"])

# Auto-Fix Announcement ID
if not df_announcement.empty:
    for idx, row in df_announcement.iterrows():
        if pd.isna(row["ID"]) or str(row["ID"]).strip() == "":
            df_announcement.at[idx, "ID"] = f"ANN-{idx + 1:03d}"
    save_data(df_announcement, ANNOUNCEMENT_FILE)

# -------------------------------------------------------------
# 2. Safe Text Cleaner for ReportLab (To Prevent Crashes/Dots)
# -------------------------------------------------------------
def clean_text(text):
    """ReportLab मध्ये मराठी अक्षरांमुळे क्रॅश/डॉट्स येऊ नयेत म्हणून सेफ्टी फिल्टर"""
    if str(text).isascii():
        return str(text)
    return str(text).encode('ascii', 'ignore').decode('ascii')

# -------------------------------------------------------------
# 3. PDF Report Generator (ReportLab Original)
# -------------------------------------------------------------
def generate_pdf():
    pdf_path = os.path.join(DATA_DIR, "Mandal_Full_Report.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CleanTitle', 
        parent=styles['Heading1'], 
        alignment=1, 
        fontSize=16, 
        fontName='Helvetica-Bold',
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'CleanSubtitle', 
        parent=styles['Normal'], 
        alignment=1, 
        fontSize=11, 
        spaceAfter=15
    )
    section_style = ParagraphStyle(
        'CleanSection', 
        parent=styles['Heading2'], 
        fontSize=12, 
        fontName='Helvetica-Bold',
        spaceBefore=10, 
        spaceAfter=5
    )

    story.append(Paragraph("Sarvajanik Ganeshotsav Mandal, Dedale", title_style))
    story.append(Paragraph("Vargani & Expense Detailed Report", subtitle_style))

    total_in = pd.to_numeric(df_vargani["Amount"], errors='coerce').sum() if not df_vargani.empty else 0
    total_out = pd.to_numeric(df_expense["Amount"], errors='coerce').sum() if not df_expense.empty else 0
    balance = total_in - total_out

    summary_data = [
        ["Total Vargani (Rs.)", "Total Expense (Rs.)", "Balance (Rs.)"],
        [f"{total_in:,.2f}", f"{total_out:,.2f}", f"{balance:,.2f}"]
    ]
    summary_table = Table(summary_data, colWidths=[170, 170, 170])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#D9EAD3")),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 15))

    # Vargani Table
    story.append(Paragraph("1. Vargani List", section_style))
    vargani_data = [["Receipt ID", "Date", "Name", "Address", "Amount (Rs.)", "Mode"]]
    if not df_vargani.empty:
        for _, row in df_vargani.iterrows():
            vargani_data.append([
                clean_text(row.get('Receipt_ID', '')),
                clean_text(str(row.get('Date', ''))[:10]),
                clean_text(row.get('Name', '')),
                clean_text(row.get('Address', '')),
                f"{row.get('Amount', 0)}",
                clean_text(row.get('Mode', ''))
            ])
    else:
        vargani_data.append(["-", "-", "No Data Available", "-", "-", "-"])

    v_table = Table(vargani_data, colWidths=[70, 80, 135, 95, 70, 50])
    v_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F3F3F3")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(v_table)
    story.append(Spacer(1, 15))

    # Expense Table
    story.append(Paragraph("2. Expense List", section_style))
    expense_data = [["Expense ID", "Date", "Category / Details", "Amount (Rs.)"]]
    if not df_expense.empty:
        for _, row in df_expense.iterrows():
            expense_data.append([
                clean_text(row.get('Expense_ID', '')),
                clean_text(str(row.get('Date', ''))[:10]),
                clean_text(row.get('Category', '')),
                f"{row.get('Amount', 0)}"
            ])
    else:
        expense_data.append(["-", "-", "No Data Available", "-"])

    e_table = Table(expense_data, colWidths=[80, 90, 230, 100])
    e_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F3F3F3")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(e_table)

    doc.build(story)
    return pdf_path

# -------------------------------------------------------------
# 4. Language & Navigation
# -------------------------------------------------------------
lang = st.sidebar.radio("🌐 भाषा / Language", ["मराठी", "English"])

T = {
    "title": {"मराठी": "🪔 सार्वजनिक गणेशोत्सव मंडळ, देदाळे", "English": "🪔 Sarvajanik Ganeshotsav Mandal, Dedale"},
    "menu": {
        "मराठी": ["📊 डॅशबोर्ड", "💰 वर्गणी नोंद (Vargani)", "📉 खर्च नोंद (Expense)", "🔍 शोधा व डिलीट करा", "📢 सूचना (Announcements)", "📑 रिपोर्ट PDF"],
        "English": ["📊 Dashboard", "💰 Donations", "📉 Expenses", "🔍 Search & Delete", "📢 Announcements", "📑 PDF Report"]
    }
}

st.sidebar.title(T["title"][lang])
choice = st.sidebar.selectbox("मेनू / Navigation", T["menu"][lang])

# -------------------------------------------------------------
# 5. Dashboard
# -------------------------------------------------------------
if choice in ["📊 डॅशबोर्ड", "📊 Dashboard"]:
    st.title(T["title"][lang])
    st.write("---")

    total_in = pd.to_numeric(df_vargani["Amount"], errors='coerce').sum() if not df_vargani.empty else 0
    total_out = pd.to_numeric(df_expense["Amount"], errors='coerce').sum() if not df_expense.empty else 0
    balance = total_in - total_out

    if balance > 5000:
        bal_bg, bal_text, bal_border = "#d4edda", "#155724", "#c3e6cb"
    elif balance >= 0:
        bal_bg, bal_text, bal_border = "#fff3cd", "#856404", "#ffeeba"
    else:
        bal_bg, bal_text, bal_border = "#f8d7da", "#721c24", "#f5c6cb"

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
            <div style="background-color:#d4edda; border:1px solid #c3e6cb; padding:15px; border-radius:10px; text-align:center;">
                <h4 style="color:#155724; margin:0;">💰 एकूण जमा वर्गणी</h4>
                <h2 style="color:#155724; margin:10px 0 0 0;">₹ {total_in:,.2f}</h2>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div style="background-color:#f8d7da; border:1px solid #f5c6cb; padding:15px; border-radius:10px; text-align:center;">
                <h4 style="color:#721c24; margin:0;">📉 एकूण खर्च</h4>
                <h2 style="color:#721c24; margin:10px 0 0 0;">₹ {total_out:,.2f}</h2>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div style="background-color:{bal_bg}; border:1px solid {bal_border}; padding:15px; border-radius:10px; text-align:center;">
                <h4 style="color:{bal_text}; margin:0;">⚖️ निव्वळ शिल्लक (Balance)</h4>
                <h2 style="color:{bal_text}; margin:10px 0 0 0;">₹ {balance:,.2f}</h2>
            </div>
        """, unsafe_allow_html=True)

    st.write("---")
    st.subheader("📢 ताज्या सूचना")
    if not df_announcement.empty:
        st.table(df_announcement[["Date", "Announcement"]].tail(5))
    else:
        st.info("कोणतीही सूचना उपलब्ध नाही.")

# -------------------------------------------------------------
# 6. Vargani (Donations)
# -------------------------------------------------------------
elif choice in ["💰 वर्गणी नोंद (Vargani)", "💰 Donations"]:
    st.header("💰 वर्गणी नोंद")

    with st.form("vargani_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        name = col1.text_input("वर्गणीदाराचे नाव")
        address = col2.text_input("राहणार (पत्ता / गाव)", value="देदाळे")
        phone = col1.text_input("फोन नंबर (10 अंकी WhatsApp Number)")
        amount = col2.number_input("रक्कम (₹)", min_value=1, step=50)
        mode = col1.selectbox("पेमेंट मोड", ["Cash", "UPI / Online"])
        submit = st.form_submit_button("वर्गणी सेव्ह करा")

        if submit:
            if name:
                rec_id = f"REC-{len(df_vargani) + 1:03d}"
                date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                new_data = {
                    "Receipt_ID": rec_id,
                    "Date": date_str,
                    "Name": name,
                    "Address": address,
                    "Phone": str(phone),
                    "Amount": amount,
                    "Mode": mode
                }
                df_vargani = pd.concat([df_vargani, pd.DataFrame([new_data])], ignore_index=True)
                save_data(df_vargani, VARGANI_FILE)
                st.success(f"✅ वर्गणी Excel मध्ये सेव्ह झाली! पावती क्र.: {rec_id}")

                if phone and len(str(phone).strip()) >= 10:
                    clean_phone = str(phone).strip().replace(" ", "").replace("+91", "")
                    msg = (
                        f"🪔 *सार्वजनिक गणेशोत्सव मंडळ, देदाळे* 🪔\n\n"
                        f"आदरणीय *{name}* ({address}),\n"
                        f"गणेशोत्सवासाठी तुमची *₹{amount}* ची वर्गणी जमा झाली आहे.\n"
                        f"पावती क्र: *{rec_id}* ({mode})\n\n"
                        f"तुमच्या मोलाच्या सहकार्याबद्दल मनःपूर्वक धन्यवाद! 🙏"
                    )
                    encoded_msg = urllib.parse.quote(msg)
                    wa_url = f"https://wa.me/91{clean_phone}?text={encoded_msg}"
                    
                    st.markdown("---")
                    st.subheader("📲 WhatsApp पावती")
                    st.markdown(f"👉 **[इथे क्लिक करून वर्गणीदाराला WhatsApp वर पावती पाठवा]({wa_url})**", unsafe_allow_html=True)
            else:
                st.error("कृपया नाव प्रविष्ट करा.")

    st.write("---")
    st.subheader("📋 जमा वर्गणी यादी")
    st.dataframe(df_vargani, use_container_width=True)

# -------------------------------------------------------------
# 7. Expense Tab
# -------------------------------------------------------------
elif choice in ["📉 खर्च नोंद (Expense)", "📉 Expenses"]:
    st.header("📉 खर्चाची नोंद")

    with st.form("expense_form", clear_on_submit=True):
        custom_category = st.text_input("खर्चाची बाब / कशासाठी खर्च झाला?", placeholder="उदा. मंडप भाडे, आरती प्रसाद, लाईटिंग इत्यादी")
        amount = st.number_input("खर्च केलेली रक्कम (₹)", min_value=1, step=10)
        submit = st.form_submit_button("खर्च नोंदवा")

        if submit:
            if custom_category:
                exp_id = f"EXP-{len(df_expense) + 1:03d}"
                date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                new_data = {
                    "Expense_ID": exp_id,
                    "Date": date_str,
                    "Category": custom_category,
                    "Amount": amount
                }
                df_expense = pd.concat([df_expense, pd.DataFrame([new_data])], ignore_index=True)
                save_data(df_expense, EXPENSE_FILE)
                st.success("✅ खर्च Excel मध्ये नोंदवला गेला व शिल्लक रक्कमेतून वजा झाला!")
                st.rerun()
            else:
                st.error("कृपया खर्चाची बाब लिहा.")

    st.subheader("📋 झालेल्या खर्चाची यादी")
    st.dataframe(df_expense, use_container_width=True)

# -------------------------------------------------------------
# 8. Search & Delete Tab
# -------------------------------------------------------------
elif choice in ["🔍 शोधा व डिलीट करा", "🔍 Search & Delete"]:
    st.header("🔍 माहिती शोधा व डिलीट करा")
    
    sub_tab1, sub_tab2 = st.tabs(["💰 वर्गणी डिलीट करा", "📉 खर्च डिलीट करा"])

    with sub_tab1:
        st.subheader("वर्गणी नोंदी डिलीट करा")
        st.dataframe(df_vargani, use_container_width=True)
        if not df_vargani.empty:
            selected_recs = st.multiselect("डिलीट करण्यासाठी पावती क्र. (Receipt IDs) निवडा:", df_vargani["Receipt_ID"].dropna().unique().tolist())
            if st.button("❌ निवडलेल्या वर्गण्या डिलीट करा", type="primary"):
                if selected_recs:
                    df_vargani = df_vargani[~df_vargani["Receipt_ID"].isin(selected_recs)]
                    save_data(df_vargani, VARGANI_FILE)
                    st.success("निवडलेल्या वर्गण्या यशस्वीरित्या डिलीट झाल्या!")
                    st.rerun()
                else:
                    st.warning("कृपया किमान एक पावती सेलेक्ट करा.")

    with sub_tab2:
        st.subheader("खर्च नोंदी डिलीट करा")
        st.dataframe(df_expense, use_container_width=True)
        if not df_expense.empty:
            selected_exps = st.multiselect("डिलीट करण्यासाठी खर्च क्र. (Expense IDs) निवडा:", df_expense["Expense_ID"].dropna().unique().tolist())
            if st.button("❌ निवडलेले खर्च डिलीट करा", type="primary"):
                if selected_exps:
                    df_expense = df_expense[~df_expense["Expense_ID"].isin(selected_exps)]
                    save_data(df_expense, EXPENSE_FILE)
                    st.success("निवडलेले खर्च यशस्वीरित्या डिलीट झाले!")
                    st.rerun()
                else:
                    st.warning("कृपया किमान एक खर्च सेलेक्ट करा.")

# -------------------------------------------------------------
# 9. Announcements Tab
# -------------------------------------------------------------
elif choice in ["📢 सूचना (Announcements)", "📢 Announcements"]:
    st.header("📢 सूचना व कार्यक्रम")

    with st.form("ann_form", clear_on_submit=True):
        ann_text = st.text_area("नवीन सूचना नोंदवा")
        submit = st.form_submit_button("प्रसिद्ध करा")

        if submit:
            if ann_text:
                ann_id = f"ANN-{len(df_announcement) + 1:03d}"
                date_str = datetime.now().strftime("%Y-%m-%d")
                new_data = {"ID": ann_id, "Date": date_str, "Announcement": ann_text}
                df_announcement = pd.concat([df_announcement, pd.DataFrame([new_data])], ignore_index=True)
                save_data(df_announcement, ANNOUNCEMENT_FILE)
                st.success("✅ सूचना पोस्ट झाली!")
                st.rerun()

    st.subheader("📋 सूचनांची यादी")
    st.dataframe(df_announcement, use_container_width=True)

    st.write("---")
    st.subheader("🗑️ सूचना डिलीट करा")
    if not df_announcement.empty:
        ann_list = [str(x) for x in df_announcement["ID"].dropna().tolist() if str(x).strip() != ""]
        selected_anns = st.multiselect("डिलीट करण्यासाठी सूचना ID निवडा:", ann_list)
        if st.button("❌ निवडलेल्या सूचना डिलीट करा", type="primary"):
            if selected_anns:
                df_announcement = df_announcement[~df_announcement["ID"].astype(str).isin(selected_anns)]
                save_data(df_announcement, ANNOUNCEMENT_FILE)
                st.success("सूचना यशस्वीरित्या डिलीट झाल्या!")
                st.rerun()
            else:
                st.warning("कृपया किमान एक सूचना सेलेक्ट करा.")

# -------------------------------------------------------------
# 10. PDF Report Generation
# -------------------------------------------------------------
elif choice in ["📑 रिपोर्ट PDF", "📑 PDF Report"]:
    st.header("📑 जमा-खर्च व वर्गणी रिपोर्ट")
    st.write("मंडळाचा संपूर्ण जमा-खर्च आणि वर्गणीची यादी खालील बटणावर क्लिक करून प्रॉपर टेबल फॉरमॅट PDF मध्ये डाऊनलोड करा:")

    if st.button("📄 PDF रिपोर्ट तयार करा"):
        pdf_file = generate_pdf()
        with open(pdf_file, "rb") as f:
            st.download_button(
                label="📥 PDF डाउनलोड करा",
                data=f,
                file_name="Mandal_Full_Report.pdf",
                mime="application/pdf"
            )