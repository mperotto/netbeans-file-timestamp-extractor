import os
import binascii
from datetime import datetime
import argparse
import re
import csv

def get_netbeans_file_history_path(netbeans_version):
    user_home = os.path.expanduser('~')
    file_history_path = os.path.join(user_home, f"AppData\\Roaming\\NetBeans\\{netbeans_version}\\var\\filehistory")
    return file_history_path

def extract_file_path(hex_content: str) -> str:
    try:
        content = bytes.fromhex(hex_content)
    except ValueError:
        return ""

    content_str = content.decode('latin-1', errors='ignore')
    printable_content = ''.join(c for c in content_str if c.isprintable())

    pattern = re.compile(r"([A-Za-z]:\\(?:[\x20-\x7E][^\x2F:*?<>|]*\\)*[\x20-\x7E][^\x2F:*?<>|]*\.[a-zA-Z0-9]+)")
    matches = pattern.findall(printable_content)
    if matches:
        return matches[0]
    else:
        return ""

def get_history_info(project_path, start_date, output_filename, file_history_path):
    try:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
    except ValueError:
        print(f'The start date "{start_date}" is not in the correct format (YYYY-MM-DD). Please provide a valid date.')
        return
    timestamp_format = '%Y-%m-%d %H:%M:%S'
    date_filter = start_datetime

    with open(output_filename, 'w', newline='') as output_file:
        csv_writer = csv.writer(output_file)
        csv_writer.writerow(['Filename', 'Modification time'])

        # Create a set to store file path and modification time combinations
        unique_rows = set()

        for root, dirs, files in os.walk(file_history_path):
            data_file_path = None
            other_files = []

            for filename in files:
                if filename == 'data':
                    data_file_path = os.path.join(root, 'data')
                else:
                    other_files.append(os.path.join(root, filename))

            if data_file_path is not None:
                try:
                    file_time = datetime.fromtimestamp(os.path.getmtime(data_file_path))
                except OSError:
                    continue

                if file_time < date_filter:
                    continue

                with open(data_file_path, 'rb') as file:
                    content = file.read()
                    hex_content = content.hex()
                    file_path = extract_file_path(hex_content)

                # Create a tuple with the file path and modification time
                row = (file_path, file_time.strftime(timestamp_format))

                # Check if the tuple is already in the set; if not, add and write to the CSV
                if row not in unique_rows:
                    unique_rows.add(row)
                    csv_writer.writerow(row)

                for other_file in other_files:
                    try:
                        other_file_time = datetime.fromtimestamp(os.path.getmtime(other_file))
                    except OSError:
                        continue
                    # Add the date filter check here
                    if other_file_time < date_filter:
                        continue
                        
                    # Create a tuple with the file path and modification time
                    row = (file_path, other_file_time.strftime(timestamp_format))

                    # Check if the tuple is already in the set; if not, add and write to the CSV
                    if row not in unique_rows:
                        unique_rows.add(row)
                        csv_writer.writerow(row)

    
if __name__ == '__main__':
    usage = 'python Netbeans_File_Timestamp_Extractor.py <project_folder> <start_date> <output_file> <netbeans_version>'
    description = 'Extracts file timestamps from NetBeans local history files.'
    epilog = 'Date format: YYYY-MM-DD. Output file format: .txt'
    parser = argparse.ArgumentParser(description=description, usage=usage, epilog=epilog)
    parser.add_argument('project_folder', type=str, help='full path to the project folder (including the drive letter)')
    parser.add_argument('start_date', type=str, help='start date for filtering (format: YYYY-MM-DD)')
    parser.add_argument('output_file', type=str, help='output file name (format: .txt)')
    parser.add_argument('netbeans_version', type=str, help='NetBeans version (e.g. 14.0)')
    args = parser.parse_args()    
    if not os.path.isdir(args.project_folder):
        print('Error: Invalid project folder path.')
    elif not re.match(r'\d{4}-\d{2}-\d{2}', args.start_date):
        print('Error: Invalid date format. Use YYYY-MM-DD.')
    elif not args.output_file.endswith('.txt'):
        print('Error: Invalid output file format. Use .txt.')
    else:
        file_history_path = get_netbeans_file_history_path(args.netbeans_version)
        get_history_info(args.project_folder, args.start_date, args.output_file, file_history_path)