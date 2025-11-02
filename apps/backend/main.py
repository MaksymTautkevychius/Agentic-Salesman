from src.telegram_bot.TelegramBot import start_telegram_bot
from src.graphs.PreProcessingGraph import generate_pre_processing_graph


if __name__ == "__main__":
     generate_pre_processing_graph()
     start_telegram_bot()