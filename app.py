import streamlit as st
from api_client import OpenLibraryClient
from reading_list_manager import ReadingListManager
from reading_guide_generator import ReadingGuideGenerator
from exceptions import BookNotFoundError, InvalidISBNError, APIRequestError, EmptySearchError

st.set_page_config(page_title="Book Discovery & Reading Companion", page_icon="📚", layout="wide")

# session_state keeps these objects alive between reruns (Streamlit reruns the
# whole script on every interaction, so anything we want to persist goes here)
if "manager" not in st.session_state:
    st.session_state.manager = ReadingListManager()
    st.session_state.manager.load()

if "search_results" not in st.session_state:
    st.session_state.search_results = []

client = OpenLibraryClient()

st.title("📚 Book Discovery & Reading Companion")

tab_search, tab_list = st.tabs(["🔍 Search", "📖 My Reading List"])

# ==================== SEARCH TAB ====================
with tab_search:
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input("Search for a book")
    with col2:
        search_type = st.selectbox("Search by", ["title", "author", "isbn"])

    if st.button("Search", type="primary"):
        try:
            st.session_state.search_results = client.search(query, search_type=search_type)
        except EmptySearchError:
            st.warning("Please enter something to search for.")
            st.session_state.search_results = []
        except InvalidISBNError as e:
            st.error(str(e))
            st.session_state.search_results = []
        except BookNotFoundError as e:
            st.info(str(e))
            st.session_state.search_results = []
        except APIRequestError as e:
            st.error(str(e))
            st.session_state.search_results = []

    for book in st.session_state.search_results:
        with st.container(border=True):
            c1, c2 = st.columns([1, 4])

            with c1:
                if book.cover_url:
                    st.image(book.cover_url, width=100)
                else:
                    st.caption("No cover available")

            with c2:
                st.subheader(book.title)
                st.write(f"**Author(s):** {', '.join(book.authors)}")
                st.write(f"**First published:** {book.first_publish_year or 'Unknown'}")
                st.write(f"**Pages:** {book.page_count or 'Unknown'}")
                if book.subjects:
                    st.caption(", ".join(book.subjects))

                b1, b2, b3, b4 = st.columns(4)

                with b1:
                    status = st.selectbox(
                        "Status", ReadingListManager.VALID_STATUSES,
                        key=f"status_{book.title}", label_visibility="collapsed"
                    )
                with b2:
                    if st.button("➕ Add to list", key=f"add_{book.title}"):
                        st.session_state.manager.add_book(book, status)
                        st.session_state.manager.save()
                        st.success(f"Added '{book.title}' as {status}.")

                with b3:
                    if st.button("✨ Generate guide", key=f"guide_{book.title}"):
                        try:
                            guide = ReadingGuideGenerator().generate(book)
                            book.reading_guide = guide
                        except (ValueError, RuntimeError) as e:
                            st.error(str(e))

                with b4:
                    if st.button("🔗 Similar books", key=f"similar_{book.title}"):
                        try:
                            similar = client.find_similar(book)
                            if similar:
                                st.session_state[f"similar_results_{book.title}"] = similar
                            else:
                                st.info("No similar books found.")
                        except APIRequestError as e:
                            st.error(str(e))

                if book.reading_guide:
                    st.markdown(f"**Summary:** {book.reading_guide.get('summary', '')}")
                    st.markdown(f"**Reading Level:** {book.reading_guide.get('reading_level', '')}")
                    st.markdown("**Discussion Questions:**")
                    for q in book.reading_guide.get("questions", []):
                        st.markdown(f"- {q}")

                similar_key = f"similar_results_{book.title}"
                if similar_key in st.session_state:
                    st.markdown("**Similar books:**")
                    for s in st.session_state[similar_key]:
                        st.write(f"- {s.title} by {', '.join(s.authors)}")

# ==================== READING LIST TAB ====================
with tab_list:
    filter_status = st.radio(
        "Filter", ["All"] + list(ReadingListManager.VALID_STATUSES), horizontal=True
    )

    books = (
        st.session_state.manager.all_books()
        if filter_status == "All"
        else st.session_state.manager.get_by_status(filter_status)
    )

    if not books:
        st.info("No books in this category yet — add some from the Search tab.")

    for book in books:
        with st.container(border=True):
            c1, c2 = st.columns([1, 4])

            with c1:
                if book.cover_url:
                    st.image(book.cover_url, width=100)

            with c2:
                st.subheader(book.title)
                st.write(f"**Status:** {book.status}")

                new_status = st.selectbox(
                    "Change status", ReadingListManager.VALID_STATUSES,
                    index=ReadingListManager.VALID_STATUSES.index(book.status),
                    key=f"change_{book.title}"
                )
                if new_status != book.status:
                    st.session_state.manager.update_status(book.title, new_status)
                    st.session_state.manager.save()
                    st.rerun()

                if st.button("🗑️ Remove from list", key=f"remove_{book.title}"):
                    st.session_state.manager.remove_book(book.title)
                    st.session_state.manager.save()
                    st.rerun()

                if book.reading_guide:
                    with st.expander("View reading guide"):
                        st.markdown(f"**Summary:** {book.reading_guide.get('summary', '')}")
                        st.markdown(f"**Reading Level:** {book.reading_guide.get('reading_level', '')}")
                        for q in book.reading_guide.get("questions", []):
                            st.markdown(f"- {q}")
