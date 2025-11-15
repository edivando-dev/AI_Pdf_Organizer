# PDF Organizer

This project is a Python script that automatically organizes PDF travel documents into a structured folder hierarchy based on their content. It uses the Gemini API to analyze the text of the PDFs and identify the cities, countries, and continents mentioned, and then moves the files to the corresponding folders.

## Features

- **PDF Text Extraction**: Extracts text from PDF files for analysis.
- **Intelligent Content Analysis**: Uses the Gemini API to identify travel destinations (cities, countries, and continents) in the text.
- **Name Normalization**: Standardizes country and city names to ensure consistent organization.
- **Automatic File Organization**: Moves files to a `DESTINATION_FOLDER/CONTINENT/COUNTRY/CITY` folder structure.
- **Detailed Logging**: Keeps logs of the process, API responses, and errors to facilitate debugging.
- **Keyword Filtering**: Allows ignoring files based on keywords present in the filename.

## Requirements

- Python 3.x
- Python Libraries:
  - `PyMuPDF`
  - `google-generativeai`
  - `python-dotenv`

## Setup and Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Install the dependencies**:
   Create a `requirements.txt` file with the following content:
   ```
   PyMuPDF
   google-generativeai
   python-dotenv
   ```
   And install it using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the API key**:
   Create a `.env` file in the root of the project and add your Gemini API key:
   ```
   GEMINI_API_KEY="your_api_key_here"
   ```

4. **Pasta Configuration**:
   Create the `PDFsForOrganizer` and `OrganizerPdfs` folders in the project root.
   - `PDFsForOrganizer`: Place the PDF files you want to organize in this folder.
   - `OrganizerPdfs`: The organized PDFs will be saved in this folder.

   **Important**: These folders are listed in the `.gitignore` file to prevent PDF files from being accidentally committed to the repository. This is a security measure to avoid exposing sensitive data. Make sure to keep this configuration.

5. **Configure the folders**:
   In the `main.py` file, adjust the `SOURCE_FOLDER` and `DESTINATION_FOLDER` variables to the desired paths:
   ```python
   SOURCE_FOLDER = r"PDFsForOrganizer"
   DESTINATION_FOLDER = r"OrganizerPdfs"
   ```

## Usage

1. **Place the PDF files** in the folder defined in `SOURCE_FOLDER`.

2. **Run the script**:
   ```bash
   python main.py
   ```

3. **Check the results**: The organized files will be in the folder defined in `DESTINATION_FOLDER`, structured by continent, country, and city.

## Logs

The script generates three log files in the `Logs/` folder:

- `general.log`: General information about the processing of each file.
- `ia_raw_responses.log`: The raw responses from the Gemini API.
- `ia_json_errors.log`: JSON parsing errors from the API responses.

## Folder Structure

- **PDFsForOrganizer/**: The source folder where you should place the PDFs to be processed.
- **OrganizerPDFs/**: The destination folder where the organized PDFs will be saved.
- **Logs/**: Contains the log files.
- **main.py**: The main script.
- **README.md**: This file.
- **.env**: The file for your environment variables (API key).
- **.gitignore**: The file that specifies which files and folders to ignore in git.
