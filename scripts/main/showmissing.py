
import sys
sys.path.append('../utils')
from db import DB

with DB() as db:
	print(db.getmissing(2020))
