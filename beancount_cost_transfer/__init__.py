
import copy
import collections

from beancount.core.number import ZERO
from beancount.core import data
from beancount.core import amount

# from beancount.parser import printer

__plugins__ = ['cost_transfer']

CostTransferError = collections.namedtuple('CostTransferError', 'source message entry')

def cost_transfer(entries, options_map, config ):
    new_entries, errors = process_entries(entries)
    return new_entries, errors

def process_entries(entries):
  new_entries = []
  errors = []
  for eindex, entry in enumerate(entries):
    if isinstance(entry, data.Transaction) and entry.flag == 'C':
      augmenting, reducing = [], []
      new_postings = []
      for pindex, posting in enumerate(entry.postings):
        if posting.units.number < ZERO:
          reducing.append(posting)
          new_postings.append(posting)
        else: 
          augmenting.append(posting)
      if len(augmenting) != 1:
        errors.append(CostTransferError(posting.meta, "Augmenting posts need to be 1", None))
      else:
        for reducing_posting in reducing:
          augmenting_posting = reducing_posting._replace(
            account=augmenting[0].account,
            units=amount.Amount(-reducing_posting.units.number, reducing_posting.units.currency),
          )
          new_postings.append(augmenting_posting)
      entry = entry._replace(postings=new_postings)

    new_entries.append(entry)

  return new_entries, errors

