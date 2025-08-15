from typing import Union
from decimal import Decimal

# Bound on float accuracy in Python 
FLOAT_PRECISION_BOUND = 54
FLOAT_EPS_BOUND = 2 ** FLOAT_PRECISION_BOUND 

I_ANGLE = Decimal(2.0)
Z_ANGLE = Decimal(1.0)
S_ANGLE = Decimal(0.5)
T_ANGLE = Decimal(0.25)

def trivial_angle_filters(
     numerator: int,
     denominator: int,
     eps) -> Union[
        tuple[int, int] | tuple[None, list]
    ]:
    '''
        Skips trivial angles
    '''
    if denominator > FLOAT_PRECISION_BOUND:
        numerator = Decimal(numerator)
        denominator = Decimal(numerator)

    approx_angle = (numerator / denominator) % I_ANGLE

    if approx_angle < eps:
        return None, []

    if abs((approx_angle % Z_ANGLE) - S_ANGLE) < eps:
        return None, ['S']

    if abs((approx_angle % S_ANGLE) - T_ANGLE) < eps:
        return None, ['T']

    return numerator, denominator

def angle_to_rational(
    angle: float,
    *,
    precision: int,
    delta: int = 3,
    ) -> (int, int): 
    '''
        Converts an angle to a rational
        TODO: This also requires increasing the precision of the initial rotation by 1 
    '''

    angle = Decimal(angle) % I_ANGLE 
    # Increasing the precision by 2 ** 3 bounded the error on the conversion to rational   
    denominator = 2 ** (precision + delta) 

    numerator = int(angle * denominator)

    if numerator < 0:
       numerator = denominator - numerator 
    
    return int(numerator), int(denominator)
