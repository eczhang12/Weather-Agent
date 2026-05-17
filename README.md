# Weather-Agent
A test-run of creating an AI agent with weather API integration.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

*** Warning: The Openweather API Key takes a couple of hours to activate

```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENWEATHER_API_KEY=your_openweathermap_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Run locally:

```bash
python main.py
```

Example prompts:

```text
What is the weather in Austin?
Give me the weather for New York
```

## Docker

Build the image:

```bash
docker build -t weather-agent .
```

Run the container:

```bash
docker run --env-file .env -it weather-agent
```
