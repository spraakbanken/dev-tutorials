import json
import time
import typing


def main():
    start = time.perf_counter()

    data_source = load_from_file("data/skbl.json")

    def doc_update(doc):
        doc["lexiconName"] = "skbl2"
        doc["lexiconOrder"] = 48
        return doc

    for doc in data_source:
        doc_update(doc)
    dump_to_file(data_source, "data/skbl2_python.json")

    end = time.perf_counter()
    print(f"Elapsed time: {end-start} s")


def load_from_file(path: str) -> typing.Any:
    with open(path) as file:
        return json.load(file)

def dump_to_file(value: list[typing.Any], path: str):
    with open(path, mode="w") as file:
        json.dump(value, file)


if __name__ == "__main__":
    main()
