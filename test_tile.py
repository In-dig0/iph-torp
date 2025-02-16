import streamlit as st
from streamlit_card import card

def show_tile(conn):
    data = [
        {"name": "Item 1", "description": "Description 1", "value": 10},
        {"name": "Item 2", "description": "Description 2", "value": 20},
        {"name": "Item 3", "description": "Description 3", "value": 30},
    ]

    cols = st.columns(3)
    for idx, item in enumerate(data):
        with cols[idx % 3]:
            st.write(f"**{item['name']}**")
            st.write(item['description'])
            st.write(f"**Value:** {item['value']}")


    data = [
        {"name": "Item 1", "description": "Description 1", "value": 10},
        {"name": "Item 2", "description": "Description 2", "value": 20},
        {"name": "Item 3", "description": "Description 3", "value": 30},
    ]

    for item in data:
        with st.container():
            st.markdown(f"""
            <div style="border: 1px solid #ccc; padding: 10px; margin: 10px; border-radius: 5px;">
                <h3>{item['name']}</h3>
                <p>{item['description']}</p>
                <p><strong>Value:</strong> {item['value']}</p>
            </div>
            """, unsafe_allow_html=True)        



    st.markdown("""
    <style>
    .card {
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        transition: 0.3s;
        width: 30%;
        border-radius: 5px;
        padding: 10px;
        margin: 10px;
        display: inline-block;
    }
    .card:hover {
        box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

    data = [
        {"name": "Item 1", "description": "Description 1", "value": 10},
        {"name": "Item 2", "description": "Description 2", "value": 20},
        {"name": "Item 3", "description": "Description 3", "value": 30},
    ]

    for item in data:
        st.markdown(f"""
        <div class="card">
            <h3>{item['name']}</h3>
            <p>{item['description']}</p>
            <p><strong>Value:</strong> {item['value']}</p>
        </div>
        """, unsafe_allow_html=True)



data = [
    {"name": "Item 1", "description": "Description 1", "value": 10},
    {"name": "Item 2", "description": "Description 2", "value": 20},
    {"name": "Item 3", "description": "Description 3", "value": 30},
]

for item in data:
    card(
        title=item['name'],
        text=item['description'],
        key=f"card_{item['name']}"
    )