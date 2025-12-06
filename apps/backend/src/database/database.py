import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv
import os,json

load_dotenv()
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

def connect_to_db() -> object:
    try:
        connection = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME
        )

        cursor = connection.cursor()

        cursor.close()
        connection.close()
        print("Connection closed.")
    except Exception as e:
        print(f"Failed to connect: {e}")


def add_user_data():
    return None

def remove_user():
    return

def modify_user_data(parameters: object):
    return

def add_message(session_id: str, message: dict) -> int:
    """
    Insert an AI message into public.n8n_chat_histories.

    :param session_id: conversation / session identifier
    :param message:    dict that will be stored as jsonb in `message` column
                       e.g. {"role": "assistant", "content": "Hello!"}
    :return:           id of the newly inserted row
    """
    try:
        with psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME,
            sslmode="require",  
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO public.chat_history (session_id, message)
                    VALUES (%s, %s)
                    RETURNING id;
                    """,
                    (str(session_id), Json(message)),
                )
                new_id = cur.fetchone()[0]
                return new_id
    except Exception as e:
        print(f"Failed to insert new message: {e}")
        raise


def get_messages_by_session_id(session_id: str):
    """
    Retrieve up to 40 chat messages for a given session from the database.

    This function establishes a new connection to the PostgreSQL database using
    the globally configured connection parameters (USER, PASSWORD, HOST, PORT,
    DBNAME, sslmode="require"), queries the `public.chat_history` table for
    rows matching the provided `session_id`, and returns the `message` column
    values.

    Parameters
    ----------
    session_id : str
        The unique identifier of the chat session whose messages should be
        retrieved.

    Returns
    -------
    list[tuple]
        A list of tuples as returned by `cursor.fetchall()`. Each tuple
        contains a single element: the `message` value for a row in
        `public.chat_history`. At most 40 rows are returned.

    Raises
    ------
    Exception
        Propagates any exception that occurs while connecting to the database
        or executing the query. The exception is logged via `print` before
        being re-raised.

    Notes
    -----
    - The results are not ordered explicitly. If ordering is important
      (e.g., by timestamp), the SQL query should include an ORDER BY clause.
    - The function uses a context manager to ensure the database connection
      and cursor are closed automatically.
    """
    try:
        with psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME,
            sslmode="require",
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT message
                    FROM public.chat_history
                    WHERE session_id = %s
                    LIMIT 40;
                    """,
                    (str(session_id),),  # 1-element tuple
                )
                output = cur.fetchall()
        return output
    except Exception as e:
        print(f"Failed to retrieve messages: {e}")
        raise


test_session_id = "session_12345"
test_message = {
    "role": "assistant",
    "content": "Hello! This is a test message3"
}

try:
    new_id = add_message(test_session_id, test_message)
    print(f"Inserted new message with ID: {new_id}")
except Exception as e:
    print(f"Error testing add_message: {e}")




test_session_id = "session_12345"  # Use an existing session_id in DB
try:
    messages = get_messages_by_session_id(test_session_id)
    print("Retrieved messages:")
    for m in messages:
        print(str(m[0]['content']))
except Exception as e:
    print(f"Error testing get_messages_by_session_id: {e}")
