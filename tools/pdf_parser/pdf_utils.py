import pdfplumber
import pandas as pd
from typing import List, Dict, Any
import re

class TariffItem:
    def __init__(self, codigo: str, descripcion: str, dai: float = None, 
                 isc: float = None, ispc: float = None, isv: float = None,
                 parent_code: str = None, level: int = None):
        self.codigo = codigo
        self.descripcion = descripcion
        self.dai = dai
        self.isc = isc
        self.ispc = ispc
        self.isv = isv
        self.parent_code = parent_code
        self.level = level

    def to_dict(self) -> Dict[str, Any]:
        return {
            'código': self.codigo,
            'descripción': self.descripcion,
            'dai': self.dai,
            'isc': self.isc,
            'ispc': self.ispc,
            'isv': self.isv,
            'parent_code': self.parent_code,
            'level': self.level
        }

def normalize_code(codigo: str) -> str:
    """
    Normalize a tariff code to its standard format.
    Examples:
        '01.01' -> '0101'
        '0101.2' -> '0101.2'
        '0101.21.00.00' -> '0101.21.00.00'
    """
    # Remove any spaces
    codigo = codigo.strip()
    
    # If it's a level 2 code (01.01), convert to 4-digit format
    if re.match(r'^\d{2}\.\d{2}$', codigo):
        return codigo.replace('.', '')
    
    return codigo

def get_parent_code(codigo: str) -> str:
    """
    Extract parent code from a given código.
    Examples:
        '0101.21.00.00' -> '0101.2' (level 4 -> level 3)
        '0101.2' -> '0101' (level 3 -> level 2)
        '0101' -> '01' (level 2 -> level 1)
        '01' -> None (level 1 -> no parent)
    """
    codigo = normalize_code(codigo)
    parts = codigo.split('.')
    
    if len(parts) <= 1:
        return None
    
    # For level 4 items (0101.21.00.00), return level 3 code (0101.2)
    if len(parts) >= 3:
        # Get the first two parts and first digit of third part
        return f"{parts[0]}{parts[1]}.{parts[2][0]}"
    
    # For level 3 items (0101.2), return level 2 code (0101)
    if len(parts) == 2:
        return parts[0]
    
    # For level 2 items (0101), return level 1 code (01)
    if len(parts) == 1 and len(parts[0]) == 4:
        return parts[0][:2]
    
    return None

def get_code_level(codigo: str) -> int:
    """
    Determine the hierarchical level of a código.
    Examples:
        '0101.21.00.00' -> 4
        '0101.2' -> 3
        '0101' -> 2
        '01' -> 1
    """
    codigo = normalize_code(codigo)
    parts = codigo.split('.')
    
    # Level 1: 01, 02, etc.
    if len(parts) == 1 and len(parts[0]) == 2:
        return 1
    
    # Level 2: 0101, 0102, etc.
    if len(parts) == 1 and len(parts[0]) == 4:
        return 2
    
    # Level 3: 0101.2, 0101.3, etc.
    if len(parts) == 2 and len(parts[1]) == 1:
        return 3
    
    # Level 4: 0101.21.00.00, etc.
    if len(parts) >= 3:
        return 4
    
    return 1  # Default to level 1 if unknown

def save_to_csv(tariff_items: List[TariffItem], output_path: str) -> None:
    """
    Save tariff items to a CSV file.
    
    Args:
        tariff_items (List[TariffItem]): List of tariff items
        output_path (str): Path to save the CSV file
    """
    df = pd.DataFrame([item.to_dict() for item in tariff_items])
    
    # Reorder columns to match the required format
    columns = ['código', 'descripción', 'dai', 'isc', 'ispc', 'isv', 'parent_code', 'level']
    df = df[columns]
    
    # Create a sorting key that ensures proper hierarchical order
    def get_sort_key(row):
        code = normalize_code(row['código'])
        level = row['level']
        
        # For level 2 items (01.01 -> 0101)
        if level == 2:
            return f"{code}_00_00"
        
        # For level 3 items (0101.2 or 0104.20)
        if level == 3:
            # Get the base code (0101 from 0101.2)
            base_code = code.split('.')[0]
            # Get the subpartida number (2 from 0101.2 or 20 from 0104.20)
            subpartida = code.split('.')[1]
            # For single digit subpartidas (2), pad with zero
            # For double digit subpartidas (20), use as is
            if len(subpartida) == 1:
                subpartida = subpartida.zfill(2)
            return f"{base_code}_{subpartida}_00"
        
        # For level 4 items (0101.21.00.00 or 0104.20.10.00)
        if level == 4:
            # Get the base code (0101 from 0101.21.00.00)
            base_code = code.split('.')[0]
            # Get the subpartida number (2 from 0101.21.00.00 or 20 from 0104.20.10.00)
            subpartida = code.split('.')[1][0]
            # Get the item number (21 from 0101.21.00.00 or 20 from 0104.20.10.00)
            item = code.split('.')[1]
            return f"{base_code}_{subpartida.zfill(2)}_{item.zfill(2)}"
        
        return code
    
    # Sort by the custom key
    df['sort_key'] = df.apply(get_sort_key, axis=1)
    df = df.sort_values('sort_key')
    df = df.drop('sort_key', axis=1)
    
    # Save with proper encoding for Spanish characters
    df.to_csv(output_path, index=False, encoding='utf-8-sig') 