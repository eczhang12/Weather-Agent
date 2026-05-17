from dotenv import load_dotenv


def print_startup_help() -> None:
    print("Weather Agent")
    print("-------------")
    print("Ask for current weather, for example:")
    print('  "What is the weather in Austin?"')
    print('  "Give me the weather for New York"')
    print()
    print("Setup:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Create .env with OPENAI_API_KEY and OPENWEATHER_API_KEY")
    print("  3. Run locally: python main.py")
    print("  4. Docker: docker build -t weather-agent .")
    print("             docker run --env-file .env -it weather-agent")
    print()
    print("Type 'quit' or 'exit' to stop.")
    print()


def missing_key(value: str, placeholder: str) -> bool:
    return not value or value == placeholder


def main() -> None:
    # Load .env before importing config-dependent modules.
    load_dotenv()

    from agent.agent import WeatherAgent
    from config import OPENAI_API_KEY, OPENWEATHER_API_KEY

    print_startup_help()

    if missing_key(OPENAI_API_KEY, "your_openai_api_key_here"):
        print("Missing OPENAI_API_KEY. Add it to your .env file before running.")
        return

    if missing_key(OPENWEATHER_API_KEY, "your_openweathermap_api_key_here"):
        print("Missing OPENWEATHER_API_KEY. Add it to your .env file before running.")
        return

    agent = WeatherAgent()

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in {"quit", "exit"}:
            print("Goodbye!")
            break

        if not user_input:
            continue

        try:
            response = agent.run(user_input)
        except Exception as exc:
            response = f"Sorry, something went wrong: {exc}"

        print(f"Agent: {response}")
        print()


if __name__ == "__main__":
    main()
