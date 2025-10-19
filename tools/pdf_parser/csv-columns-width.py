#!/usr/bin/env python3
import csv
import sys
import argparse

def find_max_column_widths(csv_filename):
    """
    Find the maximum width (in characters) of each column in a CSV file.

    Args:
        csv_filename (str): Path to the CSV file

    Returns:
        dict: Dictionary mapping column names to their maximum widths
        dict: Dictionary mapping column names to their longest content with codigo
    """
    try:
        with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
            # Use csv.DictReader to parse the CSV file
            reader = csv.DictReader(csvfile)

            # Initialize dictionary to store maximum widths
            # Start with the width of the header
            max_widths = {field: len(field) for field in reader.fieldnames}

            # Dictionary to store the longest content for specific columns
            longest_content = {"Descripcion": "", "partida": ""}
            longest_content_codigo = {"Descripcion": "", "partida": ""}

            # Iterate through each row
            for row in reader:
                for column in max_widths:
                    # Convert to string in case of numbers or other types
                    value = str(row.get(column, ''))
                    max_widths[column] = max(max_widths[column], len(value))

                    # Track longest content for Descripcion and partida
                    if column in longest_content and len(value) > len(longest_content[column]):
                        longest_content[column] = value
                        longest_content_codigo[column] = str(row.get("Codigo", ""))

            return max_widths, longest_content, longest_content_codigo

    except FileNotFoundError:
        print(f"Error: File '{csv_filename}' not found.")
        return None, None, None
    except Exception as e:
        print(f"Error processing file: {e}")
        return None, None, None

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Find maximum width of each column in a CSV file.')
    parser.add_argument('filename', help='Path to the CSV file')
    parser.add_argument('--sort', action='store_true', help='Sort columns by width (descending)')

    args = parser.parse_args()

    # Get the maximum widths and longest content
    max_widths, longest_content, longest_content_codigo = find_max_column_widths(args.filename)

    if max_widths:
        if args.sort:
            # Sort columns by width (descending)
            sorted_columns = sorted(max_widths.items(), key=lambda x: x[1], reverse=True)
            for column, width in sorted_columns:
                print(f"{column}: {width} characters")
        else:
            # Print in original column order
            for column, width in max_widths.items():
                print(f"{column}: {width} characters")

        # Print total width (useful for display planning)
        total_width = sum(max_widths.values()) + len(max_widths) - 1  # Add separators
        print(f"\nTotal width (with single-char separators): {total_width} characters")

        # Print longest content for Descripcion and partida
        print("\nLongest content in specific columns:")
        for column in longest_content:
            if longest_content[column]:
                print(f"{column} - Codigo: {longest_content_codigo[column]}")
                print(f"Content: {longest_content[column]}")
                print(f"Length: {len(longest_content[column])} characters\n")

if __name__ == "__main__":
    main()
