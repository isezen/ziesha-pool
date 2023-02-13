import streamlit as st
import base64 as _base64
from os.path import splitext as _splitext
from Ziesha.Server import Bazuka, ZoroPack, ZoroProve, UziPool


@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return _base64.b64encode(data).decode()


@st.cache(allow_output_mutation=True)
def get_img_with_href(local_img_path, target_url, text):
    img_format = _splitext(local_img_path)[-1].replace('.', '')
    bin_str = get_base64_of_bin_file(local_img_path)
    return f'''
        <a href="{target_url}">
            <img src="data:image/{img_format};base64,{bin_str}" /> {text}
        </a>'''


def header_content():
    """Header content"""
    return f'''
    <div>
    <p>
        <a href="http://65.108.193.133:8000" target="_blank" rel="nofollow">
        <i class="icon bi-water"></i> Explorer</a> |
        <a href="https://ziesha.network" target="_blank" rel="nofollow">ℤiesha.network</a> |
        <a href="https://ziesha.network/zeejs/" target="_blank" rel="nofollow">Web Wallet</a>
    </p></div>'''.replace('\n', '')


def header():
    """Header function"""

    st.markdown(f"""
    <style>
    a:link , a:visited{{
    text-decoration: none;
    }}

    a:hover,  a:active {{
    background-color: transparent;
    text-decoration: underline;
    }}

    .header {{
        position:fixed;
        padding-right: 0.5rem;
        padding-top: 0.5rem;
        margin-top: 0px;
        width:100%;
        right:0;
        top:0;
        text-align: right;
    }}
    </style>

    <div class="header">
    {header_content()}
    </div>
    """, unsafe_allow_html=True)


def footer_content():
    b, z1, z2 = Bazuka().shieldsio_link, ZoroPack(
    ).shieldsio_link, ZoroProve().shieldsio_link
    return f"""
    <p>
        <font color="#CD6155">Ziesha Pool</font> made with ❤️ by 
        <a href="https://twitter.com/pentafenolin" target="_blank" rel="nofollow noopener noreferrer">@pentafenolin</a>
        <br>
        {b} | {z1} | {z2}
    </p>""".replace('\n', '')


def footer():
    """Footer function"""
    b, z1, z2 = Bazuka().shieldsio_link, ZoroPack(
    ).shieldsio_link, ZoroProve().shieldsio_link
    st.markdown(f"""
    <style>
    a:link , a:visited{{
    text-decoration: none;
    }}

    a:hover,  a:active {{
    background-color: transparent;
    text-decoration: underline;
    }}

    .footer {{
    position: fixed;
    padding-top: 0.5rem;
    padding-right: 2.0rem;
    color: rgba(17, 17, 17, 0.4);
    left: 0;
    bottom: 0;
    width: 100%;
    text-align: right;
    }}
    </style>

    <div class="footer">
    {footer_content()}
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    footer()
