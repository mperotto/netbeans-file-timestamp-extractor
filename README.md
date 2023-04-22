# netbeans-file-timestamp-extractor

This project contains a Python script that extracts file modification timestamps from NetBeans local history. It allows users to filter the information by a specific start date and export the results to a text file.

## Requirements

- Python 3.6 or higher

## How to use

1. Clone the repository or download the `Netbeans_File_Timestamp_Extractor.py` file.
2. Open a terminal or command prompt.
3. Navigate to the directory where the `Netbeans_File_Timestamp_Extractor.py` file is located.
4. Run the following command:

```bash
python Netbeans_File_Timestamp_Extractor.py <project_folder> <start_date> <output_file> <netbeans_version>

<project_folder>: full path to the project folder (including the drive letter)
<start_date>: start date for filtering (format: YYYY-MM-DD)
<output_file>: output file name (format: .txt)
<netbeans_version>: the version of your NetBeans installation (e.g. 14.0)


