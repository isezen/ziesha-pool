# -*- coding: utf-8 -*-
"""
Ziesha Pool.

Miners Module
"""
# pylint: disable=C0103
import json as _json
import requests as _req
from requests import get as _get

PORT = 8766
IP = _get('https://api.ipify.org').content.decode('utf8')


def _request(post, where,
             url='http://127.0.0.1', port='8766'):
    """Send message to uzi-pool."""
    header = {"scheme": "http",
              "accept": "*/*",
              "Content-Type": "application/json"}
    try:
        # print(f'Trying to send message:\n{post}')
        url = f"{url}:{port}/{where}"
        req = _req.post(url=url, data=str(post), headers=header)
        data = req.content
        if req.status_code == 200:
            # print(datetime.now())
            # pprint.pprint(data)
            # print('success', req.status_code)
            return data
        print('ERROR:', req.status_code)
        return 'err'
    except (_req.RequestException, Exception) as connect_err:
        print(connect_err)
        return 'err'


def get_uzi_miner_command(token):
    """Get uzi-miner command."""
    return f"uzi-miner --pool --node {IP}:{PORT} " + \
           f"--miner-token \"{token}\" --threads $(nproc --all)"


def get():
    """Get Miner list."""
    return _json.loads(_request("", 'get-miners'))


def get_token(wallet):
    """Get token by wallet address."""
    d = get()
    tokens = list(d.keys())
    address = list(d.values())
    return tokens[address.index(wallet)]


def get_wallet_by_token(token):
    """Get Miner list."""
    return get()[token]


def get_wallets():
    """Get list of wallets joined to the pool."""
    return list(set(get().values()))


def is_registered(wallet):
    """Check wallet is registered or not."""
    return str(wallet) in get_wallets()


def number():
    """Get number of miners registered to the pool."""
    return len(get_wallets())


def register(wallet):
    """Add/register Miner to the pool."""
    if is_registered(str(wallet)):
        return get_token(str(wallet))
    result = _request(f"{{\"mpn_addr\":\"{str(wallet)}\"}}", 'add-miner')
    if result == 'err':
        raise ValueError(
            "Error in registering miner. Check your wallet address.")
    return _json.loads(result)['miner_token']


def validate_wallet(wallet):
    """Validate a Ziesha wallet address."""
    if wallet == "":
        return "Wallet address cannot be empty"
    if 0 in [w in "0123456789abcdefz" for w in wallet.lower()]:
        return "Enter a valid Ziesha MPN wallet address"
    if not 'z' in wallet:
        return "You should enter a MPN Address"
    return ""
