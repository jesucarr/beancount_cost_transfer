__copyright__ = "Copyright (C) 2015-2016  Martin Blais"
__license__ = "GNU GPLv2"

import unittest
import textwrap

from beancount import loader
from beancount.parser import cmptest
from beancount.plugins import book_conversions
from beancount.utils import test_utils


class TestCostTransfer(cmptest.TestCase):

    @loader.load_doc()
    def test_without_plugin_to_wallet_and_back(self, entries, errors, __):
        """
          option "booking_method" "FIFO"

          2015-01-01 open Assets:Exchange
          2015-01-01 open Assets:Wallet
          2015-01-01 open Assets:Bank
          2015-01-01 open Expenses:Something
          2015-09-04 * "Buy some bitcoins"
            Assets:Exchange       4 BTC {250 USD, 2015-09-04}
            Assets:Bank          -1000.00 USD
          2015-09-05 * "Buy some more bitcoins"
            Assets:Exchange       2 BTC {300 USD, 2015-09-05}
            Assets:Bank          -600.00 USD
          2015-09-10 * "Move to wallet"
            Assets:Exchange       -5 BTC {}
            Assets:Wallet         4 BTC {250 USD, 2015-09-04}
            Assets:Wallet         1 BTC {300 USD, 2015-09-05} 
          2015-09-11 * "Move to exchange"
            Assets:Wallet       -5 BTC {}
            Assets:Exchange         4 BTC {250 USD, 2015-09-04}
            Assets:Exchange         1 BTC {300 USD, 2015-09-05} 

        """
        self.assertEqualEntries("""
          2015-01-01 open Assets:Exchange
          2015-01-01 open Assets:Wallet
          2015-01-01 open Assets:Bank
          2015-01-01 open Expenses:Something
          2015-09-04 * "Buy some bitcoins"
            Assets:Exchange       4 BTC {250 USD, 2015-09-04}
            Assets:Bank          -1000.00 USD
          2015-09-05 * "Buy some more bitcoins"
            Assets:Exchange       2 BTC {300 USD, 2015-09-05}
            Assets:Bank          -600.00 USD
          2015-09-10 * "Move to wallet"
            Assets:Exchange       -4 BTC {250 USD, 2015-09-04}
            Assets:Exchange       -1 BTC {300 USD, 2015-09-05}
            Assets:Wallet         4 BTC {250 USD, 2015-09-04}
            Assets:Wallet         1 BTC {300 USD, 2015-09-05} 
          2015-09-11 * "Move to exchange"
            Assets:Wallet       -4 BTC {250 USD, 2015-09-04}
            Assets:Wallet       -1 BTC {300 USD, 2015-09-05}
            Assets:Exchange         4 BTC {250 USD, 2015-09-04}
            Assets:Exchange         1 BTC {300 USD, 2015-09-05} 
        """, entries)

    @loader.load_doc()
    def test_cost_transfer_to_wallet(self, entries, errors, __):
        """
          plugin "beancount_cost_transfer" ""
          option "booking_method" "FIFO"

          2015-01-01 open Assets:Exchange
          2015-01-01 open Assets:Wallet
          2015-01-01 open Assets:Bank
          2015-01-01 open Expenses:Something
          2015-09-04 * "Buy some bitcoins"
            Assets:Exchange       4 BTC {250 USD, 2015-09-04}
            Assets:Bank          -1000.00 USD
          2015-09-05 * "Buy some more bitcoins"
            Assets:Exchange       2 BTC {300 USD, 2015-09-05}
            Assets:Bank          -600.00 USD
          2015-09-10 C "Move to wallet"
            Assets:Exchange       -5 BTC {} 
            Assets:Wallet        

        """
        self.assertEqualEntries("""
          2015-01-01 open Assets:Exchange
          2015-01-01 open Assets:Wallet
          2015-01-01 open Assets:Bank
          2015-01-01 open Expenses:Something
          2015-09-04 * "Buy some bitcoins"
            Assets:Exchange       4 BTC {250 USD, 2015-09-04}
            Assets:Bank          -1000.00 USD
          2015-09-05 * "Buy some more bitcoins"
            Assets:Exchange       2 BTC {300 USD, 2015-09-05}
            Assets:Bank          -600.00 USD
          2015-09-10 C "Move to wallet"
            Assets:Exchange       -4 BTC {250 USD, 2015-09-04}
            Assets:Exchange       -1 BTC {300 USD, 2015-09-05}
            Assets:Wallet         4 BTC {250 USD, 2015-09-04}
            Assets:Wallet         1 BTC {300 USD, 2015-09-05} 
        """, entries)
    @loader.load_doc()
    def test_cost_transfer_to_wallet_and_back(self, entries, errors, __):
        """
          plugin "beancount_cost_transfer" ""
          option "booking_method" "FIFO"

          2015-01-01 open Assets:Exchange
          2015-01-01 open Assets:Wallet
          2015-01-01 open Assets:Bank
          2015-01-01 open Expenses:Something
          2015-09-04 * "Buy some bitcoins"
            Assets:Exchange       4 BTC {250 USD, 2015-09-04}
            Assets:Bank          -1000.00 USD
          2015-09-05 * "Buy some more bitcoins"
            Assets:Exchange       2 BTC {300 USD, 2015-09-05}
            Assets:Bank          -600.00 USD
          2015-09-10 C "Move to wallet"
            Assets:Exchange       -5 BTC {} 
            Assets:Wallet        
          2015-09-11 C "Move to exchange"
            Assets:Wallet       -5 BTC {}       
            Assets:Exchange 

        """
        self.assertEqualEntries("""
          2015-01-01 open Assets:Exchange
          2015-01-01 open Assets:Wallet
          2015-01-01 open Assets:Bank
          2015-01-01 open Expenses:Something
          2015-09-04 * "Buy some bitcoins"
            Assets:Exchange       4 BTC {250 USD, 2015-09-04}
            Assets:Bank          -1000.00 USD
          2015-09-05 * "Buy some more bitcoins"
            Assets:Exchange       2 BTC {300 USD, 2015-09-05}
            Assets:Bank          -600.00 USD
          2015-09-10 C "Move to wallet"
            Assets:Exchange       -4 BTC {250 USD, 2015-09-04}
            Assets:Exchange       -1 BTC {300 USD, 2015-09-05}
            Assets:Wallet         4 BTC {250 USD, 2015-09-04}
            Assets:Wallet         1 BTC {300 USD, 2015-09-05} 
          2015-09-11 C "Move to exchange"
            Assets:Wallet       -4 BTC {250 USD, 2015-09-04}
            Assets:Wallet       -1 BTC {300 USD, 2015-09-05}
            Assets:Exchange         4 BTC {250 USD, 2015-09-04}
            Assets:Exchange         1 BTC {300 USD, 2015-09-05} 
        """, entries)

if __name__ == '__main__':
    unittest.main()