from decimal import Decimal
from typing import NewType

Money = NewType("Money", Decimal)
Percentage = NewType("Percentage", Decimal)
