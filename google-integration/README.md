# Threat Modeling Form Integration Tool

## Overview

The Threat Modeling Form Integration Tool is designed to streamline the threat modeling process by integrating with Google Forms. This tool enables a development squad to fill out a Google Form, from which data is then extracted, parsed, and sent to a secondary tool for comprehensive threat modeling analysis.

## Features

- **Google Forms Integration**: Fetches data directly from Google Forms.
- **Data Parsing**: Converts form responses into a structured format.
- **Threat Modeling Integration**: Sends parsed data to [TaaC-AI](https://github.com/yevh/TaaC-AI) for further analysis.

## Prerequisites

- Python 3.x
- Virtual environment (recommended)
- Google Cloud credentials for accessing Google Forms and Google Drive
- [Other Tool](https://example.com/other-tool) for threat modeling analysis

## Use case

Keep in mind that this tools was designed with the use of TaaC-AI in mind, also, you need to have access to the Google Forms API to retrieve the results.

TODO: Post a blog about it

## Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/threat-modeling-integration-tool.git
   cd threat-modeling-integration-tool
   ```

2. **Google credentials**
You need to get the credentials.json to access the Google Forms API, then, login via oAuth to get the token.json to get authorization to access and retrieve the results saved in the spreadsheet.

3. **Run the script**
   ``` bash
   cd google-integration
   python3 google_forms_integration.py -u <Spreadsheet URL>
   ```