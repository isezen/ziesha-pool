#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ziesha Pool.

Ziesha mining pool
"""
# wallet = "0xa5875f8e8a4121097630c9ecab1475ded4a45a6ec98402a57c592f68910648c4"

from streamlit.components.v1 import html
from os import path
from pathlib import Path
import glob
from random import randrange
from PIL import Image, ImageEnhance

import streamlit as st  # pylint: disable=E0401
import streamlit.components.v1 as components
# https://discuss.streamlit.io/t/streamlit-option-menu-is-a-simple-streamlit-component-that-allows-users-to-select-a-single-item-from-a-list-of-options-in-a-menu/20514
from streamlit_option_menu import option_menu  # pylint: disable=E0401

import Miners as miners
from Ziesha.Server import MPNWallet
# from Faucet import send_zsh
from footer import header, footer, footer_content, header_content
from Colorize import colorize, img_to_bytes
from Ziesha.Server import Faucet
# from streamlit import javascript
from streamlit_javascript import st_javascript

POOL_NAME = "ApriPool"
POOL_CLOSED = False
WEBSITE_CLOSED = False
FAUCET_CLOSED = False
# POOL_WALLET_ADDRESS = "0xac798dca2e3275b06948c6839b9813697fc2fb60174c79e366f860d844b17202"
POOL_WALLET_ADDRESS = "z24a4a451aa41c593903f550078720d0985be2cb453d2a445927298d2e21c74778"
FAUCET_AMOUNT=1

def set_sidebar():
    sidebar_img = 'images/sidebar.png'
    gifs = glob.glob("images/gifs/*.gif")
    if len(gifs) > 0:
        sidebar_img = gifs[randrange(len(gifs))]
    if path.exists(sidebar_img):
        st.sidebar.image(sidebar_img, use_column_width=True)

def set_header_and_footer():
    """Set header and footer."""
    st.markdown("""
    <style>
        header {height: 50px; text-align: right; padding-top: 10px; padding-right: 10px;}
        footer {margin-bottom: 2rem; width: 100%; text-align: center;}
    </style>
    """, unsafe_allow_html=True)
    my_js = f"""
        window.addEventListener('load', function () {{
            var x = '{footer_content()}';
            window.parent.document.getElementsByTagName('footer')[0].innerHTML = x;
            var x = '{header_content()}';
            window.parent.document.getElementsByTagName('header')[0].innerHTML = x;
        }})
    """.replace('\n', '')
    html(f"<script>{my_js}</script>", height=0)

def main():
    """Entry point."""

    set_sidebar()

    st.markdown("""
        <style>
            #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
            #root > div:nth-child(1) > div > div > div > div > section > div > div {padding-top: 0rem;}
        </style>
        """, unsafe_allow_html=True)

    if WEBSITE_CLOSED:
        st.markdown(Path('markdown/pool_maintainance.md').read_text())
        st.markdown("<img src='data:image/png;base64,{}' class='img-fluid'>".format(
            img_to_bytes("images/maintenance.png")), unsafe_allow_html=True)
        exit()

    menu = ["Home"]
    icons = ['house']
    if not FAUCET_CLOSED:
        menu.append('Faucet')
        icons.append('water')

    par = st.experimental_get_query_params()

    try:
        sel = par['page'][0]
    except KeyError as e:
        sel = '0'
    i = int(menu.index(sel) if sel in menu else '0')

    with st.sidebar:
        choice = option_menu(
            r"ApriPool 🍑", menu, icons=icons,
            menu_icon="cast", default_index=i,
            styles={
                "nav-link-selected": {"background-color": "green"}
            })

    if choice == "Home":
        if POOL_CLOSED:
            st.markdown(Path('markdown/pool_is_closed.md').read_text())
            return

        st.info(""" ⚠️
**:red[UPDATE] (:blue[2022-02-09])**

* Pool will be **out of order** for a while since Ziesha moved to PoS.
* Ones who has a GPU will be able to register as a _prover_ to help compression process in near future.
* Every prover will be rewarded with a small amount of Ziesha.
        """)

        with st.form(key='form1'):
            wallet = st.text_input(
                '🧙🏼‍♂️ Prover Registration', placeholder='ZK (MPN) Address')
            submitted = st.form_submit_button(label='Register', disabled=True)

        if submitted:
            try:
                token = miners.register(MPNWallet(wallet))
                st.success(f"{miners.get_uzi_miner_command(token)}")
            except Exception as e:
                st.error(e)

    elif choice == "Faucet":
        st.write(
            """_Only two things are infinite, the universe and 
**Ziesha faucet**, and I'm not sure about the former._ - 
:blue[Albert Einstein]""")
        with st.form(key='form1'):
            wallet = st.text_input('Ziesha Faucet', placeholder='ZK (MPN) Address')
            submitted = st.form_submit_button(label='Send me tℤ')

        if submitted:
            try:
                result = Faucet(POOL_WALLET_ADDRESS).send(
                    wallet, FAUCET_AMOUNT)
                # result = send_zsh(wallet, POOL_WALLET_ADDRESS, FAUCET_AMOUNT)
                st.success(result)
            except Exception as e:
                st.error(e)
    else:
        st.subheader(choice)


if __name__ == '__main__':
    about = """
    # Ziesha Pool Software

    Created by Pentafenolin 2023
    http://isezen.com
    """

    st.set_page_config(
        page_title=POOL_NAME,
        page_icon="images/favico.png",
        layout='wide',
        menu_items={
            'Get help': None,
            'Report a Bug': None,
            'About': about
        },
    )
    set_header_and_footer() 
    main()
