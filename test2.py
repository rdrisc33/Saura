from test import * 
A.x = 11

from test import A  # Second imports do NOT go through, the import chain is smart enough to know not to import twice.

print(A.x)


