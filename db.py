import sqlite3
import json

# Create a single global connection
conn = sqlite3.connect('database.db', check_same_thread=False)

class Collection:
    def __init__(self, table_name):
        self.table_name = table_name
        self.cursor = conn.cursor()
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id TEXT PRIMARY KEY, data TEXT)")
        conn.commit()

    def find(self, filter_query=None):
        if filter_query is None:
            self.cursor.execute(f"SELECT data FROM {self.table_name}")
        else:
            pk_key = next(iter(filter_query))
            event_id = str(filter_query[pk_key])
            self.cursor.execute(f"SELECT data FROM {self.table_name} WHERE id=?", (event_id,))

        return [json.loads(row[0]) for row in self.cursor.fetchall()]

    def find_one(self, filter_query=None):
        res = self.find(filter_query)
        return res[0] if res else None

    def update_one(self, filter_query, update_query, upsert=False):
        # Determine the primary key from the filter_query safely
        if not filter_query:
            raise ValueError("filter_query must not be empty")

        # It's safer to extract known identifiers, but we'll try to find any key ending in Id or similar, or just the first key
        pk_key = next(iter(filter_query))
        event_id = str(filter_query[pk_key])

        event_data = update_query.get('$set', update_query)

        self.cursor.execute(f"SELECT data FROM {self.table_name} WHERE id=?", (event_id,))
        row = self.cursor.fetchone()

        class Result:
            def __init__(self):
                self.modified_count = 0
                self.upserted_id = None

        res = Result()

        if row:
            # We perform a partial update to better mimic $set semantic
            existing_data = json.loads(row[0])
            if update_query.get('$set'):
                existing_data.update(event_data)
            else:
                existing_data = event_data

            new_data_str = json.dumps(existing_data)

            if row[0] != new_data_str:
                self.cursor.execute(f"UPDATE {self.table_name} SET data=? WHERE id=?", (new_data_str, event_id))
                res.modified_count = 1
        else:
            if upsert:
                new_data_str = json.dumps(event_data)
                self.cursor.execute(f"INSERT INTO {self.table_name} (id, data) VALUES (?, ?)", (event_id, new_data_str))
                res.upserted_id = event_id

        conn.commit()
        return res

def connect(db_name, collection_name):
    # Use db_name and collection_name to create a unique table name
    table_name = f"{db_name}_{collection_name}"
    return Collection(table_name)

EVENTS_DB_CONNECTION = connect('webtic', 'events')
THEATERS_DB_CONNECTION = connect('webtic', 'theaters')
