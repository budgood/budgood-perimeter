# an UNregistered reader: reads the store file directly -> should show as 'born'
import json
def get():
    return [json.loads(l) for l in open("fake_store.jsonl")]
