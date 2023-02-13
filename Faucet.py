# -*- coding: utf-8 -*-
"""
Ziesha Pool.

Version Module
"""
# pylint: disable=C0103
import subprocess as _subp
from datetime import datetime as _dt
import streamlit as _st
from streamlit_server_state import server_state as _ss
from streamlit_server_state import server_state_lock as _ss_lock
from Ziesha.Server import PubKey, MPNWallet
import json as _json
FAUCET_COOL_DOWN_SEC = 28800 # seconds

def _run_cmd(*cmd):
    """Run commands in terminal."""
    with _subp.Popen(' '.join(cmd), stdout=_subp.PIPE, shell=True) as out:
        return out.communicate()[0].strip().decode("utf-8")

def _get_faucet():
    with _ss_lock['faucet']:
        if 'faucet' not in _ss:
            _ss['faucet'] = dict()
    return _ss['faucet']

def _add_to_faucet(addr):
    with _ss_lock['faucet']:
        _ss['faucet'][addr] = _dt.now()
    with open("faucet_wallets.json", "w") as f:
        _json.dump(_ss['faucet'], f, indent=4, sort_keys=True, default=str)

def send_zsh(to, frm, amount):
    """Send Ziesha to the address."""
    f = _get_faucet()
    a, fr, t = str(float(amount)), str(MPNWallet(frm)), str(MPNWallet(to))
    print(f)
    if t in list(f.keys()):
        d = _dt.now() - f[t]
        if d.total_seconds() < FAUCET_COOL_DOWN_SEC:
            sec = FAUCET_COOL_DOWN_SEC - d.total_seconds()
            m, s = divmod(sec, 60)
            h, m = divmod(m, 60)
            dur = f"{int(h):02d} hours {int(m):02d} min {int(s):02d} sec"
            raise ValueError(f"You have to wait {dur}.")

    ret = _run_cmd(f"bazuka wallet send --from {fr} --to {t} --amount {a}")
    if ret in ['PostMpnDepositResponse', 'PostMpnTransactionResponse']:
        _add_to_faucet(t)
        return f"Sent {amount}tℤ to {to}."
    raise ValueError(ret)
