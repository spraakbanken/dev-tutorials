// use serde_json::Value;
use std::fs::File;
// use std::io::Read;
use std::io::{BufWriter, Read};
use std::time::Instant;

use serde_json::Value;

fn main() {
    let start = Instant::now();

    let data_source = load_from_file("data/skbl.json");

    // fn doc_update(doc: &mut Value) {
    //     doc["_source"]["lexiconName"] = "skbl2".into();
    //     doc["_source"]["lexiconOrder"] = 48.into();
    // }

    // for doc in data_source.as_array_mut().expect("not an array").iter_mut() {
    //     doc_update(doc);
    // }

    dump_to_file(&data_source, "data/skbl2_rust.json");
    let elapsed = Instant::now() - start;
    println!("Elapsed time {elapsed:?}");
}

fn load_from_file(path: &str) -> Value {
    todo!("load data from {path}",)
    // let mut content = String::new();
    // File::open(path)
    //     .expect("failed to open file")
    //     .read_to_string(&mut content)
    //     .expect("failed to read file");
    // serde_json::from_str(&content).expect("failed to parse json")
}
// fn main_goal() {
//     let mut data_source = load_from_file("data/skbl.json");

//     fn doc_update(doc: &mut Value) -> &mut Value {
//         doc["_source"]["lexiconName"] = "skbl2".into();
//         doc["_source"]["lexiconOrder"] = 48.into();
//         doc
//     }

//     let updated_data = data_source
//         .as_array_mut()
//         .expect("not an array")
//         .iter_mut()
//         .map(doc_update)
//         .collect();
//     dump_to_file(&updated_data, "data/skbl2.json");
// }

// fn load_from_file(path: &str) -> Value {
//     let mut s = String::new();
//     File::open(path)
//         .expect("failed to open file")
//         .read_to_string(&mut s)
//         .expect("failed to read file");
//     serde_json::from_str(&s).expect("failed to parse json")
// }

fn dump_to_file(value: &Value, path: &str) {
    let writer = BufWriter::new(File::create(path).expect("failed to create file"));
    serde_json::to_writer(writer, value).expect("failed to serialize json")
}
