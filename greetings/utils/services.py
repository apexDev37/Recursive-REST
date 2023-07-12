"""
This module provides singleton service classes for reusable Model services.
The Singleton Pattern supports a centralized and reusable design. It avoids
unnecessary instantiation and ensures that only a single instance is reused
throughout an application.

@see  /add/reference
"""

import logging

from typing import Self

from greetings.models import Greeting

logger = logging.getLogger(__name__)

class GreetingService:
  """
  Singleton service to encapsulate custom logic for the Greeting model.
  """

  instance = None
  
  def __new__(cls) -> Self:
    if not cls.instance:
      cls.instance = super().__new__(cls)
    return cls.instance
  
  def create_and_save(custom_greeting: str) -> None:
    greeting = Greeting(greeting_text=custom_greeting)
    greeting.save()
    logger.info(f'Save custom greeting "{greeting.greeting_text}" from user.')
