import streamlit as st
from database.database import save_journal_entry, get_journal_entries

def journal_page(username):
    st.subheader("📔 My Journal")

    with st.form("journal_form"):
        entry = st.text_area("Write your thoughts or experiences here...", height=200)
        submit = st.form_submit_button("Save Entry")

        if submit and entry.strip() != "":
            save_journal_entry(username, entry)
            st.success("Your journal entry has been saved.")

    st.markdown("---")
    st.subheader("📜 Previous Entries")

    entries = get_journal_entries(username)
    if entries:
        for entry in reversed(entries):
            st.markdown(f"**{entry['timestamp']}**")
            st.write(entry["entry"])
            st.markdown("---")
    else:
        st.info("No journal entries found.")
