# OpenAI: Creating an Instagram Post with Generative AI

This repository contains a project that harnesses the power of artificial intelligence to create content for social media, specifically Instagram. The project uses OpenAI's Whisper API for transcribing audio into text summaries and OpenAI GPT for generating summaries and hashtags. It also creates impactful images with OpenAI's DALL-E, leveraging the capabilities of generative AI. The project implements the data processing and formatting flow for automating posts with InstaBot, enhancing programming skills in Python by integrating various APIs and tools.

## Project Overview
The aim of this project is to automate the process of posting an image on Instagram with content related to a podcast using only an MP3 audio file of the podcast. The project uses the latest version of the OpenAI library (1.3.9 as of December 2023), which differs significantly from the version used in the original course, with many enhancements and full functionality.

## Course Details
This project was completed as part of the course 'OpenAI and Python: Create Powerful Tools and Intelligent Chatbots with OpenAI APIs' on Alura. For more information about the course, visit [Alura](https://cursos.alura.com.br/formacao-openai-python-crie-ferramentas-chatbots-inteligentes-apis-openai-v661096).

## Objectives Achieved
- Discover the power of artificial intelligence in creating content for social media, especially Instagram
- Transcribe audio into a text summary using OpenAI's Whisper API
- Use OpenAI GPT to create summaries and generate hashtags
- Create impactful images with OpenAI's DALL-E, exploring the capabilities of generative AI
- Implement the data processing and formatting flow for automating posts with InstaBot
- Enhance Python programming skills by integrating various APIs and tools

## Technologies Used
- Python 3.11.4
- OpenAI
- Tiktoken
- Dotenv
- Pydub
- PIL
- Instabot

## Project Structure
The directory structure of the project is as follows:
```
openai-criando-uma-postagem-para-o-instagram-com-ia-generativa/
│   main.py
│   requirements.txt
│   .gitignore
│   README.md
```

## Setup Instructions
1. Clone the repository:
   ```sh
   git clone https://github.com/goosekiing/openai-criando-uma-postagem-para-o-instagram-com-ia-generativa.git
   ```
2. Navigate to the project directory:
   ```sh
   cd openai-criando-uma-postagem-para-o-instagram-com-ia-generativa
   ```
3. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```
4. Install the required libraries:
   ```sh
   pip install -r requirements.txt
   ```

## Environment Variables
Create a `.env` file in the project directory with the following variables:
- `OPENAI_API_KEY`
- `OPENAI_ORGANIZATION`
- `USER_INSTAGRAM`
- `PASSWORD_INSTAGRAM`
- `AUDIO_PATH`
- `FILE_NAME`
- `AUDIO_URL`

The OpenAI API keys should be obtained from [OpenAI's website](https://openai.com/api/). As of December 2023, new users receive $5.00 credit, sufficient for this project. Instagram variables should be filled with the user's Instagram username and password. The audio file variables are personal and can be replaced directly in the code.

## Demonstration
You can view the automated Instagram post created by this project on my Instagram:
- [Automated Instagram Post](https://www.instagram.com/p/C0-YMZ4xlvL/)
- [Explanation Video (in Portuguese)](https://www.instagram.com/p/C0-kWigtfAB/)

## Language
The language used in this project is Brazilian Portuguese (pt-br).

Feel free to explore, modify, and use this project as a foundation for your own AI-driven social media content creation!

## Author
GitHub Username: [goosekiing](https://github.com/goosekiing)
