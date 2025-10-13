from datetime import datetime

basis_mapping = {
    'ACT/365': 365,
    'ACT/360': 360
}

def year_fraction(t0: datetime, t1: datetime, basis: str):
    days = (t1 - t0).days

    if basis not in basis_mapping: 
        raise ValueError(f"Unsupported day-cout basis: {basis}")
    
    b = basis_mapping[basis]
    return days / float(b)