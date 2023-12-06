# BrowserChatGPT
BrowserChatGPT is your intelligent web companion, seamlessly integrating into your browser to provide real-time chatbot-like assistance and answers, ensuring you always have a chatbot helping you regardless of whether a website has its own.

## Table of Contents

- [BrowserChatGPT](#browserchatgpt)
  - [Table of Contents](#table-of-contents)
  - [Components](#components)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [FAQ](#faq)

## Components

The BrowserChatGPT app is comprised of the following components:

1. **apps/**: This folder houses the files necessary to render the actual app. We have a server application that runs the api that allows us to talk to the rest of the application components.

2. **browserchatgpt/**: This folder houses the main functionality that allows us to scrape data from a input website efficiently, store that data, and utilize an LLM to allow users to interact with that data.

   - `web_cache.py`: Database cache of web data to store most recently visited URLs.
   - `web_llm.py`: Implementation of LangChain LLM ([RetrievalQAWithSourcesChain](https://api.python.langchain.com/en/latest/chains/langchain.chains.qa_with_sources.retrieval.RetrievalQAWithSourcesChain.html))
   - `web_scraper_concurrent.py`: Efficient web scraper for concurrent scraping of websites and subpages.
   - `web_vector_store.py`: FAISS database to store scraped data / embeddings.

3. **chrome-extension/**: Code for packaging this application as a chrome extension.
   - `index.html`: HTML file defining the structure of the Chrome extension popup.
   - `background.js`: JavaScript file managing background tasks and handling messages/events for the extension.
   - `browserchatgpt.js`: JavaScript file facilitating communication with a web server and updating the chatbox in the extension popup.
   - `script.js`: JavaScript file managing user interactions, query submissions, and chatbox updates in the extension popup.
   - `style.css`: CSS file specifying the visual styles and layout for the Chrome extension popup.
   - `manifest.json`:JSON file serving as the manifest for the Chrome extension, configuring properties and details of the extension.

4. **tests/**: Integration tests for components in this application.

## Getting Started

### Prerequisites

Before you begin, ensure you have met the following requirements:

- You have [Python 3.9+](https://www.python.org/) installed.
- You have created an [OpenAI API Key](https://gptforwork.com/help/gpt-for-docs/setup/create-openai-api-key).

### Installation

1. Clone the repository:

    ```bash
    git@github.com:Ngrieco/BrowserChatGPT.git
    ```

2. Install virtualenv:

    ``` bash
    pip install virtualenv
    ```

3. Navigate to the root folder:
   
    ``` bash
    cd BrowserChatGPT/
    ```

4. Set up your virtual environment and set your OpenAI API Key:

    ``` bash
    virtualenv llmenv -p $(which python3.9)
    source llenv/bin/activate
    pip install .
    export OPENAI_API_KEY="YOUR_API_KEY_HERE"
    ```
5. Go to your Chrome browser and click on extensions -> developer mode -> click "load unpacked" and select the chrome-extension/ folder as a whole. Now you can use the chrome extension UI from the browser.

6. Run the server / LLM application:

    ``` bash
    python3.9 apps/server.py
    ```

7. After running the above command, you can open the extension by clicking the "C" icon in your Chrome browser while having the website you want open. At this point you will be ready to start talking to BrowserChatGPT! Enjoy!

8. To deactivate your virtual environment:
   
   ``` bash
   deactivate
   ```

## FAQ

1. **I exported my OPENAI_API_KEY to my virtual environment, but the application still isn't working. What should I do?**

    If this is an issue for you, you can try one of two things. 
    
    First off, you can navigate out of your virtual environment and export your OpenAI API Key to your global environment.

    ``` bash
    export OPENAI_API_KEY="YOUR_API_KEY_HERE"
    ```

    If that does not work either, you can add your OPENAI_API_KEY to your `~/.bashrc` file. The `~/.bashrc` is configuration file for the bash shell, which is the default on most Linux systems.

    Use nano or vim to open and edit your `~/.bashrc` file.
    ``` bash
    nano ~/.bashrc
    ```
    Add the following text to your `~/.bashrc` file.
    
    ``` bash
    export OPENAI_API_KEY="YOUR_API_KEY_HERE"
    ```
    If using nano, you can use Ctrl^O to save and Ctrl^X to exit.
