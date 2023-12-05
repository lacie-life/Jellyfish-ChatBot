import os
import openai
import streamlit as st
from streamlit_chat import message

from neo4j_driver import run_query
from english2cypher import generate_cypher
from graph2text import generate_response

import os
from neo4j import GraphDatabase

def initialize_session_state():
    if 'name' not in st.session_state:
        st.session_state['name'] = None
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = None
    if 'username' not in st.session_state:
        st.session_state['username'] = None

initialize_session_state()

# if 'generated' not in st.session_state:
#     st.session_state['generated'] = None

# Hardcoded UserID
USER_ID = "neo4j"

# On the first execution, we have to create a user node in the database.
run_query("""
MERGE (u:User {id: $userId})
""", {'userId': USER_ID})

st.set_page_config(layout="wide")
st.title("Jellyfish Chatbot")

responses = ["Tại Winmart đang có các sản phẩm nho đen mỹ, cam vàng úc, cam sành hàm yên, mận đá. Bạn cũng có thể tham khảo nước ngọt coca cola 235ml, gạo st25 vinaseed 3kg hay dầu đậu nành simply 2l. Đến ngay cửa hàng Winmart để biết thêm các ưu đãi cho các sản phẩm.",
             "Tại Winmart đang có các sản phẩm Nước giặt xả Golden king hương ban mai 3,6l giá 89.500đ/can, hộp thực phẩm Hokkaido chữ nhật/tròn 1000ml giá 51.500đ/cái. Ngoài ra, bánh trứng Karo chà bông/chà bông phô mai 26g: 27.800đ/túi, hạt nêm Chin-su thơm ngọt thịt 1kg: 42.900đ/gói và Socola Ferrero rocher 200g: 181.900đ/hộp. Cùng nhiều sản phẩm với mức giá hấp dẫn như 63.900đ/lốc giấy vệ sinh alavie blessyou 10 cuộn 2 lớp, 41.800đ/hộp màng bọc thực phẩm pe 30*100m hay 173.000đ/túi nước giặt ariel cửa trước downy oải hương 3.7kg. Ghé cửa hàng Winmart để mua sắm với mức giá ưu đãi.",
             "Hiện tại 7-eleven đang bán những sản phẩm hấp dẫn sau. Bạn có thể tham khảo bưởi da xanh tách múi, combo bánh mỳ, cơm trắng/cơm chiên. Ngoài ra còn có bánh mì cải bó xôi xá xíu, hồng trà sữa/trà sữa oolong rang ly lớn hay fuzetea+. Cuối cùng, bạn có thể mua trà sữa, trà tắc khổng lồ hay combo mì trộn tại 7-eleven. Tới cửa hàng 7-eleven để có thể xem thêm nhiều sản phẩm và ưu đãi hấp dẫn.",
             "Tại 7-eleven đang có các sản phẩm Clamelo trà tắc bưởi hồng giá dùng thử chỉ 22k, Cà phê sữa tươi 13k. Ngoài ra, mì trộn giá hẹ có giá 14k, nho đỏ úc 500gr có giá 102k hay cháo ngêu pattaya có giá 25k. Cùng nhiều sản phẩm với mức giá hấp dẫn như 79k mận Hà Nội 500g, 30k gỏi lạp thái hay 213k táo fuji Nhật (hộp 3 trái). Ghé cửa hàng Winmart để mua sắm với mức giá ưu đãi."]

cypher_output = ["MATCH path = (a:Property {value: 'product_winmart'})-[:INIT]->(b:Product) RETURN path",
                 "MATCH path = (a:Property {value: 'product_winmart'})-[:INIT]->(b:Product)-[:PRICE]->(c:Price) RETURN path",
                 "MATCH path = (a:Property {value: 'product_711'})-[:INIT]->(b:Product) RETURN path",
                 "MATCH path = (a:Property {value: 'product_711'})-[:INIT]->(b:Product) RETURN path"]


cypher_test = """MATCH path = (a:Property {value: 'promotion_711'})-[:INIT]->(b:Promotion)
RETURN path"""

def generate_context(prompt, context_data='generated'):
    context = []
    # If any history exists
    if st.session_state['generated']:
        # Add the last three exchanges
        size = len(st.session_state['generated'])
        for i in range(max(size-3, 0), size):
            context.append(
                {'role': 'user', 'content': st.session_state['user_input'][i]})
            context.append(
                {'role': 'assistant', 'content': st.session_state[context_data][i]})
    # Add the latest user prompt
    context.append({'role': 'user', 'content': str(prompt)})
    return context


# Generated natural language
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
# Neo4j database results
if 'database_results' not in st.session_state:
    st.session_state['database_results'] = []
# User input
if 'user_input' not in st.session_state:
    st.session_state['user_input'] = []
# Generated Cypher statements
if 'cypher' not in st.session_state:
    st.session_state['cypher'] = []


def get_text():
    input_text = st.text_input(
        "Ask away", "", key="input")
    return input_text


# Define columns
col1, col2 = st.columns([2, 1])

with col2:
    another_placeholder = st.empty()
with col1:
    placeholder = st.empty()
user_input = get_text()

i = 0

if user_input:
    # cypher = generate_cypher(generate_context(user_input, 'database_results'))
    # If not a valid Cypher statement
    # if not "MATCH" in cypher:
    #     print('No Cypher was returned')
    #     st.session_state.user_input.append(user_input)
    #     st.session_state.generated.append(
    #         cypher)
    #     st.session_state.cypher.append(
    #         "No Cypher statement was generated")
    #     st.session_state.database_results.append("")
    # else:
        # Query the database, user ID is hardcoded
    results = run_query(cypher_output[i], {'userId': USER_ID})
    # Harcode result limit to 10
    results = results[:10]
    # Graph2text
    answer = generate_response(generate_context(
            f"Question was {user_input} and the response should include only information that is given here: {str(results)}"))
    st.session_state.database_results.append(str(results))
    st.session_state.user_input.append(user_input)
    # st.session_state.generated.append(answer)
    # st.session_state.cypher.append(cypher_test)
    st.session_state.generated.append(responses[i])
    st.session_state.cypher.append(cypher_output[i])
    i += 1


# Message placeholder
with placeholder.container():
    if st.session_state['generated']:
        size = len(st.session_state['generated'])
        # Display only the last three exchanges
        for i in range(max(size-3, 0), size):
            message(st.session_state['user_input'][i],
                    is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))


# Generated Cypher statements
with another_placeholder.container():
    if st.session_state['cypher']:
        st.text_area("Latest generated Cypher statement",
                     st.session_state['cypher'][-1], height=240)
        


