import os
from supabase import create_client, Client
from dotenv import load_dotenv
from supabase.lib.client_options import ClientOptions


class SupaBaseClient:
    _instance = None
    _supabase = None

    def __init__(self):
        raise RuntimeError("Call instance() instead of the constructor.")

    @classmethod
    def instance(cls) -> Client:
        if cls._instance is None:
            cls._instance = cls.__new__(cls)  # Create a new instance of the class.
            load_dotenv()  # Load environment variables.
            url = os.getenv("SUPABASE_URL")  # Read the Supabase URL.
            key = os.getenv("SUPABASE_KEY")  # Read the Supabase Key.
            clientOptions = ClientOptions(postgrest_client_timeout=999999)
            cls._supabase = create_client(url, key, clientOptions)  # Initialize the Supabase client and store it.
        return cls._supabase  # Return the Supabase client.
