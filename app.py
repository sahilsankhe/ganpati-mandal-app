import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

from firebase_config import db

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="सार्वजनिक गणेशोत्सव मंडळ, देदाळे",
    page_icon="🪔",
    layout="wide"
)


# ============================================================
# FIREBASE COLLECTIONS
# ============================================================

VARGANI_COLLECTION = "vargani"
EXPENSE_COLLECTION = "expenses"
ANNOUNCEMENT_COLLECTION = "announcements"


# ============================================================
# LANGUAGE
# ============================================================

lang = st.sidebar.radio(
    "🌐 भाषा / Language",
    ["मराठी", "English"]
)


# ============================================================
# TRANSLATIONS
# ============================================================

T = {

    "title": {
        "मराठी": "🪔 सार्वजनिक गणेशोत्सव मंडळ, देदाळे",
        "English": "🪔 Sarvajanik Ganeshotsav Mandal, Dedale"
    },

    "menu": {
        "मराठी": [
            "📊 डॅशबोर्ड",
            "💰 वर्गणी नोंद (Vargani)",
            "📉 खर्च नोंद (Expense)",
            "🔍 शोधा व डिलीट करा",
            "📢 सूचना (Announcements)",
            "📑 रिपोर्ट PDF"
        ],

        "English": [
            "📊 Dashboard",
            "💰 Donations",
            "📉 Expenses",
            "🔍 Search & Delete",
            "📢 Announcements",
            "📑 PDF Report"
        ]
    }
}


st.sidebar.title(T["title"][lang])

choice = st.sidebar.selectbox(
    "मेनू / Navigation",
    T["menu"][lang]
)


# ============================================================
# FIREBASE DATA FUNCTION
# ============================================================

def get_collection_data(collection_name):

    try:

        documents = db.collection(
            collection_name
        ).stream()

        records = []

        for document in documents:

            data = document.to_dict()

            data["Firestore_ID"] = document.id

            records.append(data)

        return records

    except Exception as e:

        st.error(
            f"Firebase data load error: {e}"
        )

        return []


# ============================================================
# GENERATE NEXT ID
# ============================================================

def get_next_id(collection_name, field_name, prefix):

    try:

        documents = db.collection(
            collection_name
        ).stream()

        highest_number = 0

        for document in documents:

            data = document.to_dict()

            value = str(
                data.get(field_name, "")
            )

            if value.startswith(prefix):

                try:

                    number = int(
                        value.split("-")[-1]
                    )

                    if number > highest_number:
                        highest_number = number

                except Exception:
                    pass

        return highest_number + 1

    except Exception as e:

        st.error(
            f"ID generation error: {e}"
        )

        return 1


# ============================================================
# SAFE VALUE
# ============================================================

def safe_value(value, default=""):

    if value is None:
        return default

    try:

        if pd.isna(value):
            return default

    except Exception:
        pass

    return value


# ============================================================
# SAFE PDF TEXT
# ============================================================

def clean_text(text):

    try:

        text = str(
            safe_value(text)
        )

        if text.isascii():
            return text

        return (
            text
            .encode(
                "ascii",
                "ignore"
            )
            .decode("ascii")
        )

    except Exception:

        return ""


# ============================================================
# LOAD DATAFRAMES
# ============================================================

def load_vargani_dataframe():

    records = get_collection_data(
        VARGANI_COLLECTION
    )

    columns = [
        "Receipt_ID",
        "Date",
        "Name",
        "Location",
        "Phone",
        "Amount",
        "Mode",
        "Transaction_ID"
    ]

    if not records:

        return pd.DataFrame(
            columns=columns
        )

    df = pd.DataFrame(records)

    for column in columns:

        if column not in df.columns:

            df[column] = ""

    return df[columns]


def load_expense_dataframe():

    records = get_collection_data(
        EXPENSE_COLLECTION
    )

    columns = [
        "Expense_ID",
        "Date",
        "Category",
        "Unit",
        "Person_Name",
        "Amount",
        "Mode"
    ]

    if not records:

        return pd.DataFrame(
            columns=columns
        )

    df = pd.DataFrame(records)

    for column in columns:

        if column not in df.columns:

            df[column] = ""

    return df[columns]


def load_announcement_dataframe():

    records = get_collection_data(
        ANNOUNCEMENT_COLLECTION
    )

    columns = [
        "ID",
        "Date",
        "Announcement"
    ]

    if not records:

        return pd.DataFrame(
            columns=columns
        )

    df = pd.DataFrame(records)

    for column in columns:

        if column not in df.columns:

            df[column] = ""

    return df[columns]


# ============================================================
# LOAD ALL DATA
# ============================================================

df_vargani = load_vargani_dataframe()

df_expense = load_expense_dataframe()

df_announcement = load_announcement_dataframe()


# ============================================================
# PDF GENERATOR
# ============================================================

def generate_pdf(
    df_vargani,
    df_expense,
    df_announcement
):

    pdf_path = "Mandal_Full_Report.pdf"

    document = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=25
    )

    story = []

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        alignment=1,
        fontSize=16,
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Normal"],
        alignment=1,
        fontSize=10,
        spaceAfter=15
    )

    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        fontSize=12,
        spaceBefore=10,
        spaceAfter=6
    )

    story.append(
        Paragraph(
            "Sarvajanik Ganeshotsav Mandal, Dedale",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Vargani & Expense Report",
            subtitle_style
        )
    )

    # --------------------------------------------------------
    # TOTALS
    # --------------------------------------------------------

    if not df_vargani.empty:

        total_income = pd.to_numeric(
            df_vargani["Amount"],
            errors="coerce"
        ).fillna(0).sum()

    else:

        total_income = 0


    if not df_expense.empty:

        total_expense = pd.to_numeric(
            df_expense["Amount"],
            errors="coerce"
        ).fillna(0).sum()

    else:

        total_expense = 0


    balance = (
        total_income -
        total_expense
    )


    summary = [

        [
            "Total Vargani",
            "Total Expense",
            "Balance"
        ],

        [
            f"Rs. {total_income:,.2f}",
            f"Rs. {total_expense:,.2f}",
            f"Rs. {balance:,.2f}"
        ]

    ]


    summary_table = Table(
        summary,
        colWidths=[
            170,
            170,
            170
        ]
    )


    summary_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),

            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                1,
                colors.grey
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            )

        ])
    )


    story.append(
        summary_table
    )

    story.append(
        Spacer(1, 15)
    )


    # ========================================================
    # VARGANI REPORT
    # ========================================================

    story.append(
        Paragraph(
            "1. Vargani List",
            section_style
        )
    )


    vargani_table_data = [

        [
            "Receipt",
            "Date",
            "Name",
            "Location",
            "Amount",
            "Mode"
        ]

    ]


    for _, row in df_vargani.iterrows():

        vargani_table_data.append([

            clean_text(
                row["Receipt_ID"]
            ),

            clean_text(
                str(
                    row["Date"]
                )[:20]
            ),

            clean_text(
                row["Name"]
            ),

            clean_text(
                row["Location"]
            ),

            str(
                row["Amount"]
            ),

            clean_text(
                row["Mode"]
            )

        ])


    if len(vargani_table_data) == 1:

        vargani_table_data.append([
            "-",
            "-",
            "No Data",
            "-",
            "-",
            "-"
        ])


    vargani_table = Table(
        vargani_table_data,
        colWidths=[
            65,
            80,
            100,
            100,
            65,
            65
        ]
    )


    vargani_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            )

        ])
    )


    story.append(
        vargani_table
    )

    story.append(
        Spacer(1, 15)
    )


    # ========================================================
    # EXPENSE REPORT
    # ========================================================

    story.append(
        Paragraph(
            "2. Expense List",
            section_style
        )
    )


    expense_table_data = [

        [
            "Expense ID",
            "Date",
            "Category",
            "Unit",
            "Person",
            "Amount",
            "Mode"
        ]

    ]


    for _, row in df_expense.iterrows():

        expense_table_data.append([

            clean_text(
                row["Expense_ID"]
            ),

            clean_text(
                str(
                    row["Date"]
                )[:20]
            ),

            clean_text(
                row["Category"]
            ),

            clean_text(
                row["Unit"]
            ),

            clean_text(
                row["Person_Name"]
            ),

            str(
                row["Amount"]
            ),

            clean_text(
                row["Mode"]
            )

        ])


    if len(expense_table_data) == 1:

        expense_table_data.append([
            "-",
            "-",
            "No Data",
            "-",
            "-",
            "-",
            "-"
        ])


    expense_table = Table(
        expense_table_data,
        colWidths=[
            65,
            70,
            100,
            70,
            90,
            60,
            60
        ]
    )


    expense_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                7
            ),

            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            )

        ])
    )


    story.append(
        expense_table
    )


    document.build(
        story
    )


    return pdf_path


# ============================================================
# DASHBOARD
# ============================================================

if choice in [
    "📊 डॅशबोर्ड",
    "📊 Dashboard"
]:

    st.title(
        T["title"][lang]
    )

    st.write("---")


    # Refresh latest Firebase data

    df_vargani = load_vargani_dataframe()

    df_expense = load_expense_dataframe()

    df_announcement = load_announcement_dataframe()


    # Total income

    total_income = pd.to_numeric(
        df_vargani["Amount"],
        errors="coerce"
    ).fillna(0).sum()


    # Total expense

    total_expense = pd.to_numeric(
        df_expense["Amount"],
        errors="coerce"
    ).fillna(0).sum()


    balance = (
        total_income -
        total_expense
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "💰 एकूण जमा वर्गणी",
            f"₹ {total_income:,.2f}"
        )


    with col2:

        st.metric(
            "📉 एकूण खर्च",
            f"₹ {total_expense:,.2f}"
        )


    with col3:

        st.metric(
            "⚖️ निव्वळ शिल्लक",
            f"₹ {balance:,.2f}"
        )


    st.write("---")


    st.subheader(
        "📢 ताज्या सूचना"
    )


    if not df_announcement.empty:

        latest = df_announcement.tail(5)

        st.dataframe(
            latest[
                [
                    "Date",
                    "Announcement"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "कोणतीही सूचना उपलब्ध नाही."
        )


# ============================================================
# VARGANI
# ============================================================

elif choice in [
    "💰 वर्गणी नोंद (Vargani)",
    "💰 Donations"
]:

    st.header(
        "💰 वर्गणी नोंद"
    )


    with st.form(
        "vargani_form",
        clear_on_submit=False
    ):

        col1, col2 = st.columns(2)


        with col1:

            name = st.text_input(
                "👤 वर्गणीदाराचे नाव",
                placeholder="उदा. अमोल भाऊ"
            )


            location = st.text_input(
                "📍 Location",
                value="देदाळे"
            )


            phone = st.text_input(
                "📱 WhatsApp नंबर",
                placeholder="10 अंकी नंबर"
            )


            amount = st.number_input(
                "💰 रक्कम (₹)",
                min_value=1,
                step=50
            )


        with col2:

            mode = st.selectbox(
                "💳 Payment",
                [
                    "Cash",
                    "Online"
                ]
            )


            transaction_id = st.text_input(
                "🆔 Transaction ID",
                placeholder="Online payment असल्यास"
            )


        submit = st.form_submit_button(
            "💾 वर्गणी सेव्ह करा",
            use_container_width=True
        )


    # --------------------------------------------------------
    # SAVE VARGANI
    # --------------------------------------------------------

    if submit:

        clean_phone = (
            str(phone)
            .strip()
            .replace(
                " ",
                ""
            )
            .replace(
                "+91",
                ""
            )
        )


        # Validation

        if not name.strip():

            st.error(
                "❌ कृपया वर्गणीदाराचे नाव भरा."
            )

        elif not location.strip():

            st.error(
                "❌ कृपया Location भरा."
            )

        elif (
            len(clean_phone) != 10
            or not clean_phone.isdigit()
        ):

            st.error(
                "❌ कृपया योग्य 10 अंकी WhatsApp नंबर टाका."
            )

        elif (
            mode == "Online"
            and not transaction_id.strip()
        ):

            st.error(
                "❌ Online payment साठी Transaction ID आवश्यक आहे."
            )

        else:

            try:

                # Generate receipt

                next_number = get_next_id(
                    VARGANI_COLLECTION,
                    "Receipt_ID",
                    "MND"
                )


                receipt_id = (
                    f"MND-{next_number:04d}"
                )


                now = datetime.now()


                date_str = now.strftime(
                    "%d %B %Y"
                )


                saved_transaction_id = ""

                if mode == "Online":

                    saved_transaction_id = (
                        transaction_id.strip()
                    )


                # Firebase data

                new_vargani = {

                    "Receipt_ID":
                        receipt_id,

                    "Date":
                        date_str,

                    "Name":
                        name.strip(),

                    "Location":
                        location.strip(),

                    "Phone":
                        clean_phone,

                    "Amount":
                        float(amount),

                    "Mode":
                        mode,

                    "Transaction_ID":
                        saved_transaction_id,

                    "Created_At":
                        now.isoformat()

                }


                # Save

                db.collection(
                    VARGANI_COLLECTION
                ).document(
                    receipt_id
                ).set(
                    new_vargani
                )


                # =================================================
                # WHATSAPP MESSAGE
                # =================================================

                whatsapp_message = (

                    "🪔 *सार्वजनिक गणेशोत्सव मंडळ, देदाळे* 🙏\n\n"

                    f"प्रिय *{name.strip()}* भाऊ,\n\n"

                    f"श्री गणरायाच्या उत्सवासाठी आपण दिलेल्या "
                    f"*₹{amount:,.0f}/-* वर्गणीबद्दल मनःपूर्वक "
                    f"धन्यवाद! ❤️\n\n"

                    "आपल्या सहकार्यामुळे गणेशोत्सव अधिक "
                    "उत्साहात आणि भव्य स्वरूपात साजरा "
                    "करण्यास आम्हाला मदत मिळते.\n\n"

                    f"💰 रक्कम: ₹{amount:,.0f}/-\n"

                    f"💳 Payment: {mode}\n"

                    f"📅 दिनांक: {date_str}\n"

                    f"🧾 Receipt No.: {receipt_id}\n"
                )


                if mode == "Online":

                    whatsapp_message += (
                        f"🆔 Transaction ID: "
                        f"{transaction_id.strip()}\n"
                    )


                whatsapp_message += (
                    "\n"
                    "*गणपती बाप्पा मोरया! 🚩🙏*"
                )


                encoded_message = (
                    urllib.parse.quote(
                        whatsapp_message
                    )
                )


                whatsapp_url = (
                    "https://wa.me/91"
                    f"{clean_phone}"
                    f"?text={encoded_message}"
                )


                # =================================================
                # SUCCESS
                # =================================================

                st.success(
                    f"✅ वर्गणी यशस्वीरित्या Firebase मध्ये सेव्ह झाली!\n\n"
                    f"🧾 Receipt No.: {receipt_id}"
                )


                st.write("---")


                st.subheader(
                    "📲 WhatsApp पावती"
                )


                st.markdown(
                    f"""
                    ### 👉 [WhatsApp वर पावती पाठवा]({whatsapp_url})
                    """,
                    unsafe_allow_html=True
                )


                # Show message preview

                with st.expander(
                    "👁️ WhatsApp Message Preview"
                ):

                    st.text(
                        whatsapp_message
                    )


            except Exception as e:

                st.error(
                    f"❌ वर्गणी सेव्ह करताना Firebase error: {e}"
                )


    # ========================================================
    # VARGANI LIST
    # ========================================================

    st.write("---")

    st.subheader(
        "📋 जमा वर्गणी यादी"
    )


    df_vargani = load_vargani_dataframe()


    if not df_vargani.empty:

        st.dataframe(
            df_vargani,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "अजून कोणतीही वर्गणी नोंद नाही."
        )


# ============================================================
# EXPENSE
# ============================================================

elif choice in [
    "📉 खर्च नोंद (Expense)",
    "📉 Expenses"
]:

    st.header(
        "📉 खर्चाची नोंद"
    )


    with st.form(
        "expense_form",
        clear_on_submit=True
    ):

        col1, col2 = st.columns(2)


        with col1:

            category = st.text_input(
                "📝 खर्चाची बाब",
                placeholder="उदा. मंडप, लाईटिंग, प्रसाद"
            )


            unit = st.text_input(
                "📦 Unit",
                placeholder="उदा. 1 नग, 5 किलो, 2 दिवस"
            )


            person_name = st.text_input(
                "👤 खर्च कोणी केला?",
                placeholder="उदा. अमोल भाऊ"
            )


        with col2:

            amount = st.number_input(
                "💰 खर्चाची रक्कम (₹)",
                min_value=1,
                step=10
            )


            mode = st.selectbox(
                "💳 Payment Mode",
                [
                    "Cash",
                    "Online"
                ]
            )


        submit = st.form_submit_button(
            "💾 खर्च नोंदवा",
            use_container_width=True
        )


    # --------------------------------------------------------
    # SAVE EXPENSE
    # --------------------------------------------------------

    if submit:

        if not category.strip():

            st.error(
                "❌ कृपया खर्चाची बाब लिहा."
            )

        elif not unit.strip():

            st.error(
                "❌ कृपया Unit लिहा."
            )

        elif not person_name.strip():

            st.error(
                "❌ कृपया खर्च कोणी केला त्याचे नाव लिहा."
            )

        else:

            try:

                next_number = get_next_id(
                    EXPENSE_COLLECTION,
                    "Expense_ID",
                    "EXP"
                )


                expense_id = (
                    f"EXP-{next_number:04d}"
                )


                now = datetime.now()


                new_expense = {

                    "Expense_ID":
                        expense_id,

                    "Date":
                        now.strftime(
                            "%d %B %Y %H:%M"
                        ),

                    "Category":
                        category.strip(),

                    "Unit":
                        unit.strip(),

                    "Person_Name":
                        person_name.strip(),

                    "Amount":
                        float(amount),

                    "Mode":
                        mode,

                    "Created_At":
                        now.isoformat()

                }


                db.collection(
                    EXPENSE_COLLECTION
                ).document(
                    expense_id
                ).set(
                    new_expense
                )


                st.success(
                    f"✅ खर्च Firebase मध्ये सेव्ह झाला!\n\n"
                    f"Expense ID: {expense_id}"
                )


            except Exception as e:

                st.error(
                    f"❌ खर्च सेव्ह करताना Firebase error: {e}"
                )


    # ========================================================
    # EXPENSE LIST
    # ========================================================

    st.write("---")

    st.subheader(
        "📋 झालेल्या खर्चाची यादी"
    )


    df_expense = load_expense_dataframe()


    if not df_expense.empty:

        st.dataframe(
            df_expense,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "अजून कोणताही खर्च नोंदवलेला नाही."
        )


# ============================================================
# SEARCH & DELETE
# ============================================================

elif choice in [
    "🔍 शोधा व डिलीट करा",
    "🔍 Search & Delete"
]:

    st.header(
        "🔍 माहिती शोधा व डिलीट करा"
    )


    tab1, tab2 = st.tabs(
        [
            "💰 वर्गणी डिलीट करा",
            "📉 खर्च डिलीट करा"
        ]
    )


    # ========================================================
    # DELETE VARGANI
    # ========================================================

    with tab1:

        st.subheader(
            "💰 वर्गणी नोंदी"
        )


        df_vargani = load_vargani_dataframe()


        if not df_vargani.empty:

            st.dataframe(
                df_vargani,
                use_container_width=True,
                hide_index=True
            )


            receipt_ids = (
                df_vargani[
                    "Receipt_ID"
                ]
                .dropna()
                .astype(str)
                .tolist()
            )


            selected_receipts = st.multiselect(
                "🧾 डिलीट करण्यासाठी Receipt No. निवडा:",
                receipt_ids
            )


            if st.button(
                "❌ निवडलेल्या वर्गण्या डिलीट करा",
                type="primary",
                key="delete_vargani_button"
            ):

                if not selected_receipts:

                    st.warning(
                        "कृपया किमान एक Receipt No. निवडा."
                    )

                else:

                    try:

                        for receipt_id in selected_receipts:

                            db.collection(
                                VARGANI_COLLECTION
                            ).document(
                                receipt_id
                            ).delete()


                        st.success(
                            "✅ निवडलेल्या वर्गण्या डिलीट झाल्या."
                        )


                        st.rerun()


                    except Exception as e:

                        st.error(
                            f"❌ Delete error: {e}"
                        )

        else:

            st.info(
                "डिलीट करण्यासाठी वर्गणी उपलब्ध नाही."
            )


    # ========================================================
    # DELETE EXPENSE
    # ========================================================

    with tab2:

        st.subheader(
            "📉 खर्च नोंदी"
        )


        df_expense = load_expense_dataframe()


        if not df_expense.empty:

            st.dataframe(
                df_expense,
                use_container_width=True,
                hide_index=True
            )


            expense_ids = (
                df_expense[
                    "Expense_ID"
                ]
                .dropna()
                .astype(str)
                .tolist()
            )


            selected_expenses = st.multiselect(
                "🧾 डिलीट करण्यासाठी Expense ID निवडा:",
                expense_ids
            )


            if st.button(
                "❌ निवडलेले खर्च डिलीट करा",
                type="primary",
                key="delete_expense_button"
            ):

                if not selected_expenses:

                    st.warning(
                        "कृपया किमान एक Expense ID निवडा."
                    )

                else:

                    try:

                        for expense_id in selected_expenses:

                            db.collection(
                                EXPENSE_COLLECTION
                            ).document(
                                expense_id
                            ).delete()


                        st.success(
                            "✅ निवडलेले खर्च डिलीट झाले."
                        )


                        st.rerun()


                    except Exception as e:

                        st.error(
                            f"❌ Delete error: {e}"
                        )

        else:

            st.info(
                "डिलीट करण्यासाठी खर्च उपलब्ध नाही."
            )


# ============================================================
# ANNOUNCEMENTS
# ============================================================

elif choice in [
    "📢 सूचना (Announcements)",
    "📢 Announcements"
]:

    st.header(
        "📢 सूचना व कार्यक्रम"
    )


    with st.form(
        "announcement_form",
        clear_on_submit=True
    ):

        announcement = st.text_area(
            "📝 नवीन सूचना नोंदवा",
            height=150,
            placeholder="उदा. उद्या सकाळी 9 वाजता मंडळाची बैठक आहे."
        )


        submit = st.form_submit_button(
            "📢 प्रसिद्ध करा",
            use_container_width=True
        )


    if submit:

        if not announcement.strip():

            st.error(
                "❌ कृपया सूचना लिहा."
            )

        else:

            try:

                next_number = get_next_id(
                    ANNOUNCEMENT_COLLECTION,
                    "ID",
                    "ANN"
                )


                announcement_id = (
                    f"ANN-{next_number:04d}"
                )


                now = datetime.now()


                new_announcement = {

                    "ID":
                        announcement_id,

                    "Date":
                        now.strftime(
                            "%d %B %Y"
                        ),

                    "Announcement":
                        announcement.strip(),

                    "Created_At":
                        now.isoformat()

                }


                db.collection(
                    ANNOUNCEMENT_COLLECTION
                ).document(
                    announcement_id
                ).set(
                    new_announcement
                )


                st.success(
                    "✅ सूचना Firebase मध्ये पोस्ट झाली!"
                )


                st.rerun()


            except Exception as e:

                st.error(
                    f"❌ सूचना save error: {e}"
                )


    # ========================================================
    # ANNOUNCEMENT LIST
    # ========================================================

    st.write("---")

    st.subheader(
        "📋 सूचनांची यादी"
    )


    df_announcement = (
        load_announcement_dataframe()
    )


    if not df_announcement.empty:

        st.dataframe(
            df_announcement,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "अजून कोणतीही सूचना उपलब्ध नाही."
        )


    # ========================================================
    # DELETE ANNOUNCEMENT
    # ========================================================

    st.write("---")

    st.subheader(
        "🗑️ सूचना डिलीट करा"
    )


    if not df_announcement.empty:

        announcement_ids = (
            df_announcement[
                "ID"
            ]
            .dropna()
            .astype(str)
            .tolist()
        )


        selected_announcements = st.multiselect(
            "डिलीट करण्यासाठी सूचना ID निवडा:",
            announcement_ids
        )


        if st.button(
            "❌ निवडलेल्या सूचना डिलीट करा",
            type="primary",
            key="delete_announcement_button"
        ):

            if not selected_announcements:

                st.warning(
                    "कृपया किमान एक सूचना निवडा."
                )

            else:

                try:

                    for announcement_id in selected_announcements:

                        db.collection(
                            ANNOUNCEMENT_COLLECTION
                        ).document(
                            announcement_id
                        ).delete()


                    st.success(
                        "✅ निवडलेल्या सूचना डिलीट झाल्या."
                    )


                    st.rerun()


                except Exception as e:

                    st.error(
                        f"❌ Delete error: {e}"
                    )


# ============================================================
# PDF REPORT
# ============================================================

elif choice in [
    "📑 रिपोर्ट PDF",
    "📑 PDF Report"
]:

    st.header(
        "📑 मंडळाचा संपूर्ण रिपोर्ट"
    )


    st.write(
        "वर्गणी, खर्च आणि शिल्लक रकमेचा PDF रिपोर्ट तयार करा."
    )


    if st.button(
        "📄 PDF रिपोर्ट तयार करा",
        use_container_width=True
    ):

        try:

            df_vargani = load_vargani_dataframe()

            df_expense = load_expense_dataframe()

            df_announcement = (
                load_announcement_dataframe()
            )


            pdf_file = generate_pdf(
                df_vargani,
                df_expense,
                df_announcement
            )


            with open(
                pdf_file,
                "rb"
            ) as file:

                st.download_button(

                    label="📥 PDF डाउनलोड करा",

                    data=file.read(),

                    file_name="Mandal_Full_Report.pdf",

                    mime="application/pdf",

                    use_container_width=True

                )


        except Exception as e:

            st.error(
                f"❌ PDF तयार करताना error: {e}"
            )
