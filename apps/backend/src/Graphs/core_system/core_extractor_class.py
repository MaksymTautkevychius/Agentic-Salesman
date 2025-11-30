from pydantic import BaseModel, Field
from typing import List, Optional

class CoreExtractor:
    name : str = Optional(Field(description='Extract the actual customer name if provided'))
    budget_amount : str = Optional(Field(description='Extract the budget amount or range if provided Example: 50k, 25-30k, $50000'))
    is_watch_inquiry: bool = Optional(Field(description='True if user is asking about a specific watch, price, or showing watch image'))
    has_name: bool = Optional(Field(description='True if user provided their actual name (not just [sure], [ok] or non-name responses)'))
    watch_names: str = Optional(Field(description="""
Extract the specific watch details from the given text.
Return only the fields listed below. If a field is not explicitly mentioned, leave it blank — do not infer or guess.

Fields to extract:

Brand

Model

Reference Number

Dial Color

Size

Nickname

Bracelet Type

Condition

Other (any extra relevant details not covered above)

Example Output:
Brand: Rolex
Model: 
Reference Number: 116500LN
Dial Color: White
Size: 40mm
Nickname: Panda
Bracelet Type: Oyster
Condition: Unworn / Pre-Owned
Other: Anything else mentioned
"""))
    time : str = Optional(Field(description='Time when User want to buy the Watch ASAP/in a few Weeks/Now e.t.c.'))
    is_already_given: str = Optional(Field(description='When the watch with all the parameters is already given and is the same as was given before'))
    ready_to_purchase: str = Optional(Field(description=
"""
Is True when user answered to all questions regarding the watch and is ready to make a deal or send the transfer
It has to be false if user asks another question after confirming
For questions such as "Market price for the Rolex Day-Date Champagne 40mm, full set box & papers, is around 135k aed 
Thats about 36.8k usd 
Would this price range work for you" GIVE FALSE
"""))
    telegram : bool = Optional(Field(description='True if user says or answers simmilar:  I do not have telegram , I have problems with telegram'))

