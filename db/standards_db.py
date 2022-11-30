# POPULATES THE DATABASE WITH THE STANDARIZATION KEYWORDS
from tqdm import tqdm
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.sqlqueries import engine
from tools.create_standard import add_standard

# getting the list of standards

engine.connect()
query = '''
SELECT query FROM gvolume
ORDER BY volumerank
'''
response = engine.execute(query).fetchall()
standard_list= [x[0] for x in response]

# Populating the standardvolume table

add_standard(standard_list[0], False)
for i in tqdm(range(len(standard_list)-1)):
    add_standard(standard_list[i], standard_list[i+1])
