use std::time::Instant;

use serde_json::Value;

fn main() {
    let start = Instant::now();

    let data_source = json_iter::load_from_file("data/skbl.json");

    fn doc_update(mut doc: Value) -> Value {
        doc["lexiconName"] = "skbl2".into();
        doc["lexiconOrder"] = 48.into();
        doc
    }

    let update_data = data_source.map(|doc| doc_update(doc));
    json_iter::dump_to_file(update_data, "data/skbl2_rust_stream.json");
    println!("Elapsed time {:?}", start.elapsed());
}

pub mod json_iter {
    use serde_json::Value;
    use std::io::BufWriter;
    use std::{fs::File, io::BufReader};
    use struson::reader::{JsonReader, JsonStreamReader};
    use struson::writer::{JsonStreamWriter, JsonWriter};

    pub fn load_from_file<'de, T>(path: &str) -> impl Iterator<Item = T>
    where
        T: serde::Deserialize<'de>,
    {
        let file = File::open(path).unwrap();
        let reader = BufReader::new(file);
        let mut json_reader = JsonStreamReader::new(reader);

        json_reader.begin_array().unwrap();
        std::iter::from_fn(move || {
            if json_reader.has_next().unwrap() {
                let t: T = json_reader.deserialize_next().unwrap();
                Some(t)
            } else {
                None
            }
        })
    }

    pub fn dump_to_file<I, T>(iter: I, path: &str)
    where
        I: Iterator<Item = T>,
        T: serde::Serialize,
    {
        let writer = BufWriter::new(File::create(path).expect("failed to create file"));
        let mut json_writer = JsonStreamWriter::new(writer);
        json_writer.begin_array().unwrap();
        for val in iter {
            json_writer.serialize_value(&val).unwrap();
        }
        json_writer.end_array().unwrap();
        json_writer.finish_document().unwrap();
    }
}
