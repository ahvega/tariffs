import os
import sys
import re
import pdfplumber
import pandas as pd
from pdf_utils import TariffItem, get_parent_code, get_code_level, save_to_csv, normalize_code

def clean_description(desc: str) -> str:
    """
    Clean the description by removing unnecessary parts.
    """
    # Remove "(Según Art." and everything after it
    desc = re.sub(r'\(Según Art\..*$', '', desc, flags=re.MULTILINE)
    return desc.strip()

def extract_tariff_items(pdf_path: str) -> list:
    """
    Extract tariff items from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        List[TariffItem]: List of tariff items with hierarchical information
    """
    tariff_items = []
    current_section = None
    current_level2 = None
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # First try to extract text normally
            text = page.extract_text()
            if not text:
                continue
            
            lines = text.split('\n')
            current_description = []
            
            for line in lines:
                if not line.strip():
                    continue
                
                # Pattern for level 2 sections (e.g., "01.01 CABALLOS, ASNOS...")
                level2_pattern = r'^(\d{2}\.\d{2})\s+(.+)$'
                level2_match = re.match(level2_pattern, line.strip())
                
                if level2_match:
                    # If we have accumulated description text, add it to the previous item
                    if current_description and tariff_items:
                        tariff_items[-1].descripcion += ' ' + ' '.join(current_description)
                        current_description = []
                    
                    current_section = {
                        'code': level2_match.group(1),
                        'description': clean_description(level2_match.group(2))
                    }
                    # Add level 2 section as a tariff item
                    current_level2 = current_section['code']
                    tariff_items.append(TariffItem(
                        codigo=normalize_code(current_section['code']),
                        descripcion=current_section['description'],
                        level=2,
                        parent_code=current_section['code'].split('.')[0]
                    ))
                    continue
                
                # Pattern for level 3 subpartidas (e.g., "0101.2 Caballos" or "0104.10 Bovinos")
                level3_pattern = r'^(\d{4}\.\d{1,2})\s+(.+)$'
                level3_match = re.match(level3_pattern, line.strip())
                
                if level3_match:
                    # If we have accumulated description text, add it to the previous item
                    if current_description and tariff_items:
                        tariff_items[-1].descripcion += ' ' + ' '.join(current_description)
                        current_description = []
                    
                    current_section = {
                        'code': level3_match.group(1),
                        'description': clean_description(level3_match.group(2))
                    }
                    # Add level 3 subpartida as a tariff item
                    tariff_items.append(TariffItem(
                        codigo=current_section['code'],
                        descripcion=current_section['description'],
                        level=3,
                        parent_code=current_level2.replace('.', '') if current_level2 else None
                    ))
                    continue
                
                # Pattern for level 4 items (e.g., "0101.21.00.00 Reproductores...")
                level4_pattern = r'(\d{4}\.\d{2}\.\d{2}\.\d{2})\s+(.+?)\s+(\d+|-)\s+(-|\d+(?:\.\d+)?)\s+(-|\d+(?:\.\d+)?)\s+(-|\d+(?:\.\d+)?)'
                level4_match = re.match(level4_pattern, line.strip())
                
                if level4_match:
                    # If we have accumulated description text, add it to the previous item
                    if current_description and tariff_items:
                        tariff_items[-1].descripcion += ' ' + ' '.join(current_description)
                        current_description = []
                    
                    codigo = level4_match.group(1)
                    descripcion = clean_description(level4_match.group(2))
                    dai = float(level4_match.group(3))/100 if level4_match.group(3) != '-' else None
                    isc = float(level4_match.group(4))/100 if level4_match.group(4) != '-' else None
                    ispc = float(level4_match.group(5))/100 if level4_match.group(5) != '-' else None
                    isv = float(level4_match.group(6))/100 if level4_match.group(6) != '-' else None
                    
                    # Get the level 3 parent code
                    parent_code = get_parent_code(codigo)
                    
                    tariff_items.append(TariffItem(
                        codigo=codigo,
                        descripcion=descripcion,
                        dai=dai,
                        isc=isc,
                        ispc=ispc,
                        isv=isv,
                        level=4,
                        parent_code=parent_code
                    ))
                    continue
                
                # If the line doesn't match any pattern and we have a current item,
                # it might be a continuation of the description
                if tariff_items and not line.strip().startswith(('01.', '0101.', '0102.', '0103.', '0104.')):
                    current_description.append(line.strip())
            
            # If we have accumulated description text at the end of the page, add it to the last item
            if current_description and tariff_items:
                tariff_items[-1].descripcion += ' ' + ' '.join(current_description)
    
    return tariff_items

def main():
    if len(sys.argv) < 2:
        pdf_path = "GRAVAMEN A LA IMPORTACIÓN 2022.pdf"
        if os.path.exists(pdf_path):
            print(f"Usando archivo predeterminado: {pdf_path}")
        else:
            print(f"Error: No se encontró el archivo predeterminado {pdf_path}")
        print("Usage: python parse_tariffs.py <pdf_filename>")
        sys.exit(1)
    else:
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} not found")
        sys.exit(1)
    
    try:
        print(f"Processing {pdf_path}...")
        
        # Extract items with hierarchical information
        tariff_items = extract_tariff_items(pdf_path)
        
        # Generate output filename
        output_path = "aranceles.csv"
        
        print(f"Found {len(tariff_items)} tariff items")
        save_to_csv(tariff_items, output_path)
        print(f"Results saved to {output_path}")
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 