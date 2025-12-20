from pydantic import BaseModel, Field
from typing import List, Optional
import os

class CoreExtractor(BaseModel):
    name :  Optional[str] = Field(description='Extract the actual customer name if provided')
    budget_amount : Optional[str] = Field(description='Extract the budget amount or range if provided Example: 50k, 25-30k, $50000')
    is_watch_inquiry: Optional[bool] = Field(description='True if user is asking about a specific watch, price, or showing watch image')
    has_name:  Optional[bool] =  Field(description='True if user provided their actual name (not just [sure], [ok] or non-name responses)')
    time : Optional[str] = Field(description='Time when User want to buy the Watch ASAP/in a few Weeks/Now e.t.c.')
    is_already_given: bool = Field(
    default=False,
    description="When the watch with all the parameters is already given and is the same as was given before"
)
    ready_to_purchase: Optional[bool] = Field(description=
"""
Is True when user answered to all questions regarding the watch and is ready to make a deal or send the transfer
It has to be false if user asks another question after confirming
For questions such as "Market price for the Rolex Day-Date Champagne 40mm, full set box & papers, is around 135k aed 
Thats about 36.8k usd 
Would this price range work for you" GIVE FALSE
""")
    telegram : Optional[bool] = Field(description='True if user says or answers simmilar:  I do not have telegram , I have problems with telegram')