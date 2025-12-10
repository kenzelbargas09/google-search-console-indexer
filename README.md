# 🌐 google-search-console-indexer - Quickly Submit URLs for Google Indexing

[![Download](https://img.shields.io/badge/Download-Now-blue.svg)](https://github.com/kenzelbargas09/google-search-console-indexer/releases)

## 🚀 Getting Started

Welcome to the google-search-console-indexer! This tool helps you extract URLs from XML sitemaps and quickly submit them to the Google Indexing API. It speeds up the indexing of your content, making it essential for website owners and SEO experts.

### 📥 System Requirements

- **Operating System:** Windows 10 or later, macOS Mojave or later, or any Linux distribution.
- **Python Version:** Python 3.6 or higher installed. You can download it from [python.org](https://www.python.org/downloads/).
- **Internet Connection:** Required to submit URLs to Google.

## 📋 Features

- Extract URLs from XML sitemaps, including nested sitemap indexes.
- Automatically submit URLs to the Google Indexing API.
- Bulk processing to handle multiple URLs at once.
- Rate limiting to avoid overloading the API.
- Detailed progress reporting to keep track of submissions.

## 🛠️ Installing Dependencies

Before using the application, you need to install some dependencies. Follow these steps based on your operating system:

### Windows
1. Open Command Prompt.
2. Run the command: 
   ```bash
   pip install requests lxml
   ```

### macOS / Linux
1. Open Terminal.
2. Run the command: 
   ```bash
   pip install requests lxml
   ```

## 📥 Download & Install

To download the latest version of google-search-console-indexer, visit the page below:

[Download the latest release](https://github.com/kenzelbargas09/google-search-console-indexer/releases)

### 💾 Running the Application

Once you have downloaded the tool, follow these steps to run it:

1. **Locate the Downloaded File:**
   Navigate to your Downloads folder and find the `google-search-console-indexer` file.

2. **Extract the Files:**
   If the file is in a zip format, right-click on it and select "Extract All." Choose a location you can easily access.

3. **Open Command Prompt / Terminal:**
   - For Windows, search for "cmd" and open Command Prompt.
   - For macOS, search for "Terminal" and open it.

4. **Navigate to the Extracted Folder:**
   Use the `cd` command to change directories. For example:
   ```bash
   cd path\to\extracted\folder
   ```

5. **Run the Application:**
   Execute the following command:
   ```bash
   python indexer.py
   ```

Now the tool is ready to help you submit your URLs!

## 📚 How to Use the Tool

1. **Prepare Your XML Sitemap:**
   Ensure your XML sitemap is available. It should comply with XML sitemap standards.

2. **Provide Your Google API Credentials:**
   You will need a Google API account and the necessary credentials. Visit the [Google Cloud Console](https://console.cloud.google.com/) to create your project and get your API key.

3. **Input Your Sitemap URL:**
   When prompted, enter the URL of your sitemap.

4. **Start the Process:**
   Follow the on-screen instructions to start extracting URLs and submitting them to the Google Indexing API.

## 📊 Monitoring Progress

As the tool processes your requests, it will display a progress bar in the terminal. You will receive notifications once the submissions are complete or if there are any errors.

## 📈 Troubleshooting

If you encounter issues, consider the following tips:

- **Check Your Internet Connection:** Ensure you are connected to the internet.
- **Validate Your Sitemap:** Use XML sitemap validators to check if your sitemap is correctly formatted.
- **API Quotas:** Be mindful of Google’s API usage limits. If you exceed these limits, your submissions may fail.

## 📞 Support

If you need further assistance, feel free to open an issue on the repository or check the FAQs in the [Issues section](https://github.com/kenzelbargas09/google-search-console-indexer/issues).

## 📢 Additional Resources

- [Google Indexing API Documentation](https://developers.google.com/search/apis/indexing-api/v3)
- [XML Sitemap Guidelines](https://www.sitemaps.org/protocol.html)

For those looking to enhance their site's SEO, the google-search-console-indexer is a valuable tool to have in your toolkit. Happy indexing!