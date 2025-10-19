# Honduras Tariff Items Parser

This project provides tools to extract and parse Partidas Arancelarias (tariff items) from PDF documents into structured CSV format.

## Setup

1. Create a virtual environment:

```bash
python -m venv venv
```

2. Activate the virtual environment:

- Windows:

```bash
.\venv\Scripts\activate
```

- Unix/MacOS:

```bash
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Place your PDF file containing the Partidas Arancelarias in the project directory and run:

```bash
python src/parse_tariffs.py <pdf_filename>
```

The script will generate a CSV file with the parsed tariff items.

## Output Format

The CSV file will contain the following columns:

- Partida (Tariff Item Code)
- Descripción (Description)
- Gravamen (Tariff Rate)
- Additional relevant data as found in the PDF
