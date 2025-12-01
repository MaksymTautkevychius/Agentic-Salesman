from src.telegram_handler.telegram_input_handler import start_telegram_bot
from src.graphs.pre_processing_graph import generate_pre_processing_graph



if __name__ == "__main__":
     generate_pre_processing_graph()
     start_telegram_bot()