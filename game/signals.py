"""File used to implement signals"""
"""Every class subclasses the Exception class"""

class GameOver(Exception):
    pass

class DoublePass(GameOver):
    pass

class InvalidMove(ValueError):
    pass

class InducesSuicide(InvalidMove):
    pass

class OccupiedCase(InvalidMove):
    pass

class BreakingKo(InvalidMove):
    pass

class BreakingSuperKo(InvalidMove):
    pass
