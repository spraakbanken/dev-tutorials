import time

from json_streams import json_iter


def main():
    start = time.perf_counter()
    data_source = json_iter.load_from_file("data/skbl.json")

    def doc_update(doc):
        doc["_source"]["lexiconName"] = "skbl2"
        doc["_source"]["lexiconOrder"] = 48
        return doc

    update_data = (doc_update(doc) for doc in data_source)
    json_iter.dump_to_file(update_data, "data/skbl2_python_stream.json")
    end = time.perf_counter()
    print(f"Elapsed time: {end-start} s")


if __name__ == "__main__":
    main()
