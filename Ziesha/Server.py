# -*- coding: utf-8 -*-
"""
Ziesha Pool.

Miners Module
"""
# pylint: disable=C0103

from pathlib import Path as _Path
from psutil import Process as _Process
import subprocess as _subp
import json as _json
# from pprint import pprint as _pprint
from datetime import datetime as _dt
from .Core import _Singleton, run_cmd
from .Core import Key as _Key
from .Core import PubKey as _PubKey
from .Core import MPNWallet as _MPNWallet
from .Exceptions import FaucetDurationError as _FaucetDurationError


class Process(_Process):
    """Process class."""

    def __init__(self, name, filter=None):
        """
        Init Process class.

        Args:
            name (str): Process name.
            filter (str): Process filter.
        Raises:
            ValueError: If process is not running.
        """
        if isinstance(filter, str):
            filter = [filter]
        super().__init__(int(Process._get_pid(name, filter)))

    @staticmethod
    def _filter(ls, filter):
        """
        Filter list.

        Args:
            ls (dict): List to filter.
            filter (list): Filter list.
        Returns:
            dict: Filtered list.
        """
        if filter is None:
            return ls
        if not isinstance(filter, list):
            filter = [filter]
        return {pid: arg for pid, arg in ls.items()
                if all(f in arg for f in filter)}

    @staticmethod
    def _get_args(pid):
        """
        Get process arguments.

        Args:
            pid (int): Process id.
        Returns:
            dict: Process arguments.
        """
        if isinstance(pid, list):
            return {k: v for p in pid for k, v in Process._get_args(p).items()}
        return {pid: run_cmd("ps", "-p", pid, "-o", "args=")}

    @staticmethod
    def _get_pid(name, filter=None):
        """
        Get process id.

        Args:
            name (str): Process name.
            filter (str): Process filter.
        Returns:
            int: Process id.
        """
        pid = run_cmd("pgrep", name).split('\n')
        if len(pid) == 1 and pid[0] == '':
            raise ValueError(f"'{name}' is not running")
        args = Process._filter(Process._get_args(pid), filter)
        if len(args) == 0:
            raise ValueError(f"'{name}' is not running")
        return list(args.keys())[0]

    @property
    def id(self):
        """Get process id."""
        return self.pid

    @property
    def path(self):
        """Get process path."""
        return run_cmd("readlink", "-f", f"/proc/{self.id}/exe")

    @property
    def cmd(self):
        """Get process command."""
        return ' '.join(self.cmdline())

    @property
    def opts(self):
        """Get process options."""
        a = self.cmdline()
        return {a[a.index(i)].replace('--', ''): a[a.index(i) + 1]
                for i in a if i.startswith('--')}

    @property
    def elapsed(self):
        """Get process elapsed time."""
        return run_cmd("ps", "-p", str(self.id), "-o", "etime=")


class ZieshaTool:
    """Ziesha Tool class."""

    def __init__(self, name, color='green'):
        """
        Init ZieshaTool class.

        Args:
            name (str): Tool name.
            color (str): Badge color.
        Raises:
            ValueError: If tool is not a Ziesha tool.
            ValueError: If tool is not installed.
        """
        tools = ['bazuka', 'zoro', 'uzi-pool', 'uzi-miner']
        if name not in tools:
            raise ValueError(f"'name' must be one of {tools}")
        path = run_cmd("which", name)
        if path == '':
            raise ValueError(f"'{name}' is not installed")
        self._path = _Path(path)
        self.name = name
        self.color = color

    def __repr__(self):
        """Return string representation of ZieshaTool class."""
        txt = f"{self.name.title()} (v{self.version}):\n"
        if self.is_running:
            txt += f"  PID  : {self.proc.id}\n"
            txt += f"  PATH : {self.path}\n"
            txt += f"  OPTS :\n"
            for k, v in self.proc.opts.items():
                txt += f"    {k} : {v}\n"
        else:
            txt += " Not running\n"
        return txt

    @property
    def is_running(self):
        """Check if tool is running."""
        try:
            return self.proc.is_running
        except ValueError:
            return False

    @property
    def path(self):
        """Get tool path."""
        return self._path

    @property
    def home(self):
        """Get tool home."""
        return _Path.home()

    @property
    def opts(self):
        """Get running arguments."""
        return self.proc.opts

    @property
    def is_installed(self):
        """Check if tool is installed."""
        return not run_cmd("which", self.name) == ''

    @property
    def github(self):
        """Get link to GitHub."""
        return f"https://github.com/ziesha-network/{self.name}"

    def _get_shieldsio(self, name):
        """Get shields.io badge."""
        col = self.color if self.is_running else 'red'
        name = name.replace('-', '--') if '-' in name else name
        url = "https://img.shields.io/badge"
        return f"{url}/{name}-{self.version}-{col}"

    @property
    def shieldsio(self):
        """Get shields.io badge."""
        return self._get_shieldsio(self.name.title())

    @property
    def shieldsio_link(self):
        """Get shields.io badge with link."""
        hint = 'Running' if self.is_running else 'Not Running'
        return f'<a href="{self.github}" title="{hint}" target="_blank" rel="nofollow">' + \
               f'<img src="{self.shieldsio}"' + \
               f'alt="Installed {self.name.title()} version"></a>'

    @property
    def version(self):
        """Get tool version."""
        ret = run_cmd(self.name, "--version")
        if self.name != 'bazuka':
            ret = ret.split('\n')[-1]
        return ret.split(' ')[-1]

    @property
    def proc(self):
        """Get process."""
        return Process(self.name)


class Key(_Key):
    """Key class."""

    def _run_(self, *args):
        """Run wallet command."""
        return run_cmd(Bazuka().name, 'wallet', 'send', *args)

    def send(self, to, amount):
        """
        Send Ziesha to another address.
        
        Args:
            to (str): Address to send Ziesha to.
            amount (float): Amount of Ziesha to send.

        Returns:
            bool: True if successful.

        Raises:
            TypeError: If amount is not a number.
            ValueError: If Wallwet does not have an amount.
            ValueError: If amount is less than or equal to 0.
            ValueError: If amount is greater than the balance.
            ValueError: If the send operation is not successful.
        """
        if self.amount is None:
            raise ValueError("Wallet does not have an amount.")
        if not isinstance(amount, (str, int, float)):
            raise TypeError("Amount must be a number.")
        amount = float(amount)

        if amount <= 0:
            raise ValueError("Amount must be greater than 0.")

        if amount > self.amount:
            raise ValueError("Amount must be less than or equal to the "
                             "balance.")

        if not isinstance(to, Key):
            to = Key(to)

        ret = self._run_('--from', self, '--to',
                         to, '--amount', str(amount))
        print(self)
        print(ret)
        return
        if ret in ['PostMpnDepositResponse', 'PostMpnTransactionResponse']:
            return True
        raise ValueError(ret)


class PubKey(_PubKey, Key):
    pass


class MPNWallet(_MPNWallet, Key):
    pass


class Wallet(metaclass=_Singleton):
    """Bazuka Wallet class."""

    def __init__(self):
        """
        Init Bazuka Wallet class.

        Args:
            tool (Bazuka): Bazuka tool.
        """
        self._bazuka = Bazuka()

    def _run_(self, *args):
        """Run wallet command."""
        return run_cmd(self._bazuka.name, "wallet", *args)

    def __repr__(self):
        """Return string representation of Bazuka Wallet class."""
        return self._run_("info")

    @property
    def address(self):
        """Get wallet addresses."""
        addresses = []
        amounts = []
        info = self._run_("info")
        for add in info.split('\n\n'):
            for i in add.split('\n'):
                if i.startswith('Address'):
                    addresses.append(i.split()[-1])
                if i.startswith('#'):
                    amounts.append(float(i.split()[-1][:-1]))
        return dict(zip(addresses, amounts))

    def _get_key(self, index=0, cls=_PubKey):
        """Get key."""
        info = self._run_("info").split('\n\n')[index].split('\n')
        ad = info[2].split()[-1]
        am = info[3].split()[-1][:-1]
        return cls(ad, am)

    @property
    def pub(self):
        """Get wallet PubKey object."""
        return self._get_key()

    @property
    def mpn(self):
        """Get wallet MPNWallet object."""
        return self._get_key(1, MPNWallet)

    @property
    def info(self):
        """Get wallet info."""
        return self._run_("info")

    def new_token(self, name, symbol, supply, decimals, fee, mintable=False):
        """Create new token."""
        cmd = ["new-token"]
        if mintable:
            cmd.append('--mintable')
        cmd += ['--name', name, '--symbol', symbol, '--supply', supply,
                '--decimals', decimals, '--fee', fee]
        return self._run_(*cmd)

    def add_token(self, id):
        """Add token."""
        return self._run_("add-token", '--id', id)

    def resend_pending(self):
        """Resend pending transactions."""
        return self._run_("resend-pending")

    def reset(self):
        """Reset wallet."""
        return self._run_("reset")


class Node(metaclass=_Singleton):
    """Bazuka Node class."""

    def __init__(self):
        """
        Init Bazuka Node class.

        Args:
            tool (Bazuka): Bazuka tool.
        """
        self._bazuka = Bazuka()

    def __repr__(self):
        """Return string representation of Bazuka Node class."""
        return run_cmd(f"{self._tool.name} node status")

    def start(self, flags='', opts=''):
        """Start node."""
        args = ' '.join([self._tool.name, "node", "start",
                         flags, opts]).strip()

        p = _subp.Popen(
            args, shell=True, stdout=_subp.PIPE, stderr=_subp.STDOUT)
        for line in iter(p.stdout.readline, ''):
            print(line.strip().decode("utf-8")),
        retval = p.wait()
        # res = _subp.run(args.split(' '), capture_output=True)
        # return res
        # print(res.stdout)
        # return run_cmd(self._tool.name, "node", "start", flags, opts)


class Bazuka(ZieshaTool, metaclass=_Singleton):
    """Bazuka class."""

    def __init__(self):
        self._files = {
            'bazuka.yaml': _Path('~/.bazuka.yaml').expanduser(),
            'bazuka.wallet': _Path('~/.bazuka.wallet').expanduser()}
        super().__init__('bazuka')

    @property
    def proc(self):
        return Process(self.name, filter='node start')

    @property
    def node(self):
        return Node()

    @property
    def wallet(self):
        """Get wallet."""
        return Wallet()





class ZoroProve(ZieshaTool, metaclass=_Singleton):
    def __init__(self):
        super().__init__('zoro')
        self._filter = 'prove'

    @property
    def shieldsio(self):
        """Get shields.io badge."""
        return self._get_shieldsio(f"{self.name.title()}{self._filter.title()}")
    @property
    def proc(self):
        return Process(self.name, filter=self._filter)


class ZoroPack(ZieshaTool, metaclass=_Singleton):
    def __init__(self):
        super().__init__('zoro')
        self._filter = 'pack'

    @property
    def shieldsio(self):
        """Get shields.io badge."""
        return self._get_shieldsio(f"{self.name.title()}{self._filter.title()}")

    @property
    def proc(self):
        return Process(self.name, filter=self._filter)


class Miner:
    def __init__(self, wallet, token):
        self._wallet = wallet
        self._token = token

    def __repr__(self):
        return f"{self._wallet} - {self._token}"

    @property
    def wallet(self):
        return self._wallet

    @property
    def token(self):
        return self._token


class PoolMiners(metaclass=_Singleton):
    """Miner class."""

    def __init__(self):
        self._file = _Path('~/.uzi-pool-miners').expanduser()
        self.load()

    def __repr__(self):
        return str(self._miners)

    @property
    def miners(self):
        return self._miners

    @property
    def count(self):
        return len(self._miners)

    def load(self):
        """Load Miner list."""
        self._miners = {
            i['token']: Miner(i['mpn_addr']['pub_key'][0], i['token'])
            for i in _json.load(self._file.open('r'))}


class UziPool(ZieshaTool, metaclass=_Singleton):
    def __init__(self):
        self._files = {
            'uzi_pool_miners': _Path('~/.uzi-pool-miners').expanduser(),
            'uzi-pool-history': _Path('~/.uzi-pool-history').expanduser()}
        super().__init__('uzi-pool')

    @property
    def proc(self):
        return Process(self.name, filter='--node')


class UziMiner(ZieshaTool, metaclass=_Singleton):
    def __init__(self):
        super().__init__('uzi-miner')

    @property
    def proc(self):
        return Process(self.name, filter='--node')


class Faucet(metaclass=_Singleton):

    def __init__(self, wallet, COOL_DOWN_SEC=None):
        self._file = _Path('~/.faucet.history').expanduser()
        self._wallet = MPNWallet(wallet)
        if COOL_DOWN_SEC is None:
            self._COOL_DOWN_SEC = 28800  # seconds
        self.load()

    def __repr__(self):
        """Return string representation of Faucet class."""
        return str(self._wallet_list)

    @property
    def wallet(self):
        """Return Faucet Wallet."""
        return self._wallet

    @property
    def hist(self):
        """Return Faucet History."""
        return self._wallet_list

    def load(self):
        """Load Faucet History."""
        self._wallet_list = _json.load(self._file.open(
            'r')) if self._file.exists() else dict()
        for k, v in self._wallet_list.items():
            self._wallet_list[MPNWallet(k)] = _dt.fromisoformat(v)

    def save(self):
        """Save Faucet History."""
        self._wallet_list = {k: v for k, v in self._wallet_list.items()
                             if (_dt.now() - v).total_seconds() < self._COOL_DOWN_SEC}
        _json.dump(self._wallet_list, self._file.open(
            'w'), indent=4, sort_keys=False, default=str)

    def send(self, to, amount):
        a, f, t = str(float(amount)), self._wallet, MPNWallet(to)
        if t in self._wallet_list.keys():
            d = _dt.now() - self._wallet_list[t]
            if d.total_seconds() < self._COOL_DOWN_SEC:
                raise _FaucetDurationError(self._COOL_DOWN_SEC, d.total_seconds())
        ret = run_cmd(f"bazuka wallet send --from {f} --to {t} --amount {a}")
        print(ret)
        if ret in ['PostMpnDepositResponse', 'PostMpnTransactionResponse']:
            self._wallet_list[t] = _dt.now()
            self.save()
            return f"Sent {amount}tℤ to {to}."
        raise ValueError(ret)
