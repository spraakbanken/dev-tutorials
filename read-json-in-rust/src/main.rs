use std::fs::File;
use std::io::BufWriter;

use std::io::Read;
use std::time::Instant;

use serde_json::Value;

fn main() {
    let start = Instant::now();

    let mut data_source = load_from_file("data/skbl.json");

    fn doc_update(doc: &mut Value) {
        doc["lexiconName"] = "skbl2".into();
        doc["lexiconOrder"] = 48.into();
    }

    for doc in &mut data_source {
        doc_update(doc);
    }
    dump_to_file(&data_source, "data/skbl2_rust.json");
    println!("Elapsed time {:?}", start.elapsed());
}

fn load_from_file(path: &str) -> Vec<Value> {
    let mut content = String::new();
    File::open(path)
        .expect("a valid path")
        .read_to_string(&mut content)
        .expect("a valid JSON file");
    serde_json::from_str(&content).expect("successfully parsed json")
}

fn dump_to_file(value: &[Value], path: &str) {
    let writer = BufWriter::new(File::create(path).expect("failed to create file"));
    serde_json::to_writer(writer, value).expect("failed to serialize json")
}
