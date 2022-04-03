import datetime
from dateutil.relativedelta import *

use_date = datetime.datetime.now()
use_date = str(use_date + relativedelta(months=+1)).split(" ")[0]
print(use_date)
