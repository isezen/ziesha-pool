import streamlit as st
# from streamlit.report_thread import REPORT_CONTEXT_ATTR_NAME
from streamlit.runtime.scriptrunner.script_run_context import SCRIPT_RUN_CONTEXT_ATTR_NAME
from threading import current_thread
from contextlib import contextmanager
from io import StringIO
import sys
import logging
import time


padding_top = 0
padding_bottom = 10
padding_left = 1
padding_right = 10
# max_width_str = f'max-width: 100%;'
st.markdown(f'''
<style>
    .reportview-container .sidebar-content {{
        padding-top: {padding_top}rem;
    }}
    .reportview-container .main .block-container {{
        padding-top: {padding_top}rem;
        padding-right: {padding_right}rem;
        padding-left: {padding_left}rem;
        padding-bottom: {padding_bottom}rem;
    }}
</style>
''', unsafe_allow_html=True)

@contextmanager
def st_redirect(src, dst):
    placeholder = st.empty()
    output_func = getattr(placeholder, dst)

    with StringIO() as buffer:
        old_write = src.write

        def new_write(b):
            if getattr(current_thread(), SCRIPT_RUN_CONTEXT_ATTR_NAME, None):
                buffer.write(b + '')
                output_func(buffer.getvalue() + '')
            else:
                old_write(b)

        try:
            src.write = new_write
            yield
        finally:
            src.write = old_write


@contextmanager
def st_stdout(dst):
    "this will show the prints"
    with st_redirect(sys.stdout, dst):
        yield


@contextmanager
def st_stderr(dst):
    "This will show the logging"
    with st_redirect(sys.stderr, dst):
        yield


def demo_function():
    """
    Just a sample function to show how it works.
    :return:
    """
    for i in range(100):
        logging.warning(f'Counting... {i}')
        time.sleep(2)
        print('Time out...')


if __name__ == '__main__':
    with st_stdout("success"), st_stderr("code"):
        demo_function()