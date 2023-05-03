# Read JSON in Rust

[Rust](https://www.rust-lang.org/) is a system-level programming language that is compiled ahead of time (like Java, C, C++ ,...).

In this tutorial we are going to read JSON and possible parse it.

You can follow along at your own computer or at [replit.com](https://replit.com)

## Python example

We begin by looking at an example from karp-backend-5 where we read and update an JSON file.

```python
import json
import time
import typing


def main():
    start = time.perf_counter()

    data_source = load_from_file("data/skbl.json")

    def doc_update(doc):
        doc["_source"]["lexiconName"] = "skbl2"
        doc["_source"]["lexiconOrder"] = 48
        return doc

    for doc in data_source:
        doc_update(doc)

    dump_to_file(data_source, "data/skbl2_py.json")

    elapsed  = time.perf_counter() - start
    print(f"Elapsed time: {elapsed} s")


def load_from_file(path: str) -> typing.Any:
    with open(path) as file:
        return json.load(file)

def dump_to_file(value: list[typing.Any], path: str):
    with open(path, mode="w") as file:
        json.dump(value, file)


if __name__ == "__main__":
    main()
```

When running it we get this:
```bash
> python read_json_in_rust.py
Elapsed time: 0.7634601149984519 s
```
Memory usage:
![Memory usage of python program](./python_memory_usage.png)

## Rewrite that in rust

We begin with that timings,

### Setting up a cargo project

`cargo` is Rust's package manager, we can create a project:
```bash
> cargo new read-json-in-rust
    Created binary (application) `read-json-in-rust` package
```

If we `cd` into the directory we can run our application:
```bash
> cd read-json-in-rust
> cargo run
   Compiling read-json-in-rust v0.1.0 (.../read-json-in-rust)
    Finished dev [unoptimized + debuginfo] target(s) in 0.85s
     Running `target/debug/read-json-in-rust`
Hello, world!
```

Working correctly, and this is the code:
```rust
fn main() {
    println!("Hello, world!");
}
```

We have a function (`fn`) `main` that uses a macro (invoked with `!` after) to print `Hello, world!` with new-line to `stdout`.
The macro is because rust functions can't handle variadic functions, but rust macros can.

### Add timings

```rust

use std::time::Instant;

fn main() {
    let start = Instant::now();

    let elapsed = Instant::now() - start;
    println!("Elapsed time {elapsed:?}");
}
```

All variable must be declared with `let`.
The notation `"{elapsed:?}"` tells rust to use the `Debug` formatter for `Instant`, that is implemented for the most types, but for many types the standard `Display` formatter isn't not implemented (so is the case for `Instant`).

### function load_from_file

So let's add the function `load_from_file`.
Let us begin to sketch a solution.

```rust
fn main() {
    let start = Instant::now();

    let data_source = load_from_file("data/skbl.json");
    ...
}

fn load_from_file(path: &str) {
    todo!("load data from {}", path)
}
```

**Notes:** `str` is the string slice type in rust, and `&` is a reference (borrow) to, in this case, a string slice. So `load_from_file` borrows the string slice from it's caller.

## Serde

In rust the de-facto standard for serialization and deserialization is [serde](https://serde.rs), and especially the **_crate_** [`serde_json`](https://crates.io/crates/serde_json). Let's add it to our project:
```bash
> cargo add serde_json
    Updating crates.io index
      Adding serde_json v1.0.96 to dependencies.
             Features:
             + std
             - alloc
             - arbitrary_precision
             - float_roundtrip
             - indexmap
             - preserve_order
             - raw_value
             - unbounded_depth
```

Great, we added `serde_json` to our project. The `cargo add` also lists the features that are available for this crate, but we don't need to bother about that yet.

## Read JSON

We begin by looking at an example from [json-streams-py](https://github.com/spraakbanken/json-streams-py) where we read and update an JSON file.

```python
from json_streams import json_iter


def main():
    data_source = json_iter.load_from_file("data/skbl.json")

    def doc_update(doc):
        doc["_source"]["lexiconName"] = "skbl2"
        doc["_source"]["lexiconOrder"] = 48
        return doc

    update_data = (doc_update(doc) for doc in data_source)
    json_iter.dump_to_file(update_data, "data/skbl2.json")


if __name__ == "__main__":
    main()
```

## Load JSON
Let us begin to sketch the  solution.

```rust
fn main() {
    let start = Instant::now();

    let data_source = load_from_file("data/skbl.json");
}

fn load_from_file(path: &str) {
    todo!("load data from {}", path)
}
```

**Notes:** `str` is the string slice type in rust, and `&` is a reference (borrow) to, in this case, a string slice. So `load_from_file` borrows the string slice from it's caller.
We're using the `todo` macro to crash the program with an optional message.

And running it, gives us:

```bash
> cargo run
   Compiling read-json-in-rust v0.1.0 (.../read-json-in-rust)
    Finished dev [unoptimized + debuginfo] target(s) in 0.39s
     Running `target/debug/read-json-in-rust`
thread 'main' panicked at 'not yet implemented: load data from data/skbl.json', src/main.rs:29:5
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```

Our application panics with the message `not yet implemented: load data from data/skbl.json`
- panics is one of rust's way of handling errors, abort the program if something fails

And running it, gives us:

```bash
> cargo run
    Updating crates.io index
  Downloaded ryu v1.0.13
  Downloaded serde v1.0.160
  Downloaded serde_json v1.0.96
  Downloaded itoa v1.0.6
  Downloaded 4 crates (278.9 KB) in 0.38s
   Compiling serde v1.0.160
   Compiling serde_json v1.0.96
   Compiling ryu v1.0.13
   Compiling itoa v1.0.6
   Compiling read-json-in-rust v0.1.0 (.../read-json-in-rust)
warning: unused variable: `data_source`
 --> src/main.rs:2:9
  |
2 |     let data_source = load_from_file("data/skbl.json");
  |         ^^^^^^^^^^^ help: if this is intentional, prefix it with an underscore: `_data_source`
  |
  = note: `#[warn(unused_variables)]` on by default

warning: `read-json-in-rust` (bin "read-json-in-rust") generated 1 warning (run `cargo fix --bin "read-json-in-rust"` to apply 1 suggestion)
    Finished dev [unoptimized + debuginfo] target(s) in 4.21s
     Running `target/debug/read-json-in-rust`
thread 'main' panicked at 'not yet implemented: load data from data/skbl.json', src/main.rs:6:5
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```

Ok, what happend?
1. `cargo` downloads the needed crates to compile our crate. For us it means that `serde_json` and all dependencies for it is downloaded.
2. `cargo` then compiles everything and then links everything together.
    - `cargo` emits a warning that we don't use the variable `data_source` in main.
    - These steps is also available as `cargo build`.
3. `cargo` runs our application
4. our application panics with the message `not yet implemented: load data from data/skbl.json`
    - panics is one of rust's way of handling errors, abort the program if something fails


Ok, and now to the implementation

```rust
fn load_from_file(path: &str) -> Value {
    let mut s = String::new();
    File::open(path)
        .expect("failed to open file")
        .read_to_string(&mut s)
        .expect("failed to read file");
    serde_json::from_str(&s).expect("failed to parse json")
}
```

So what is new?
1. We added return type `-> Value`, that is a type for JSON Value:s from serde_json.
2. We create a new String and mark it as **mutable**.
3. We open the file given in `path`
    - this can fail, and now we panic if there was an error
    - we read the file and store it in our created string, for this we need a mutable borrow.
    - this can also fail, and we panic if again.
4. We use parse our JSON with serde_json by passing a string slice from our string `S` and panic if the parsing fails.
5. The last statment of a function is implicitly returned. A statment is a expression without `;`.

We also add the following `use`-expressions (imports):
```rust
use serde_json::Value;
use std::fs::File;
```

And let's run it:
```bash
> cargo run
   Compiling read-json-in-rust v0.1.0 (/home/kristoffer/projekt/sb/dev-tutorials/read-json-in-rust)
error[E0599]: no method named `read_to_string` found for struct `File` in the current scope
   --> src/main.rs:10:31
    |
10  |     File::open(path).unwrap().read_to_string(&mut s).unwrap();
    |                               ^^^^^^^^^^^^^^ method not found in `File`
    |
   ::: /home/kristoffer/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/src/rust/library/std/src/io/mod.rs:754:8
    |
754 |     fn read_to_string(&mut self, buf: &mut String) -> Result<usize> {
    |        -------------- the method is available for `File` here
    |
    = help: items from traits can only be used if the trait is in scope
help: the following trait is implemented but not in scope; perhaps add a `use` for it:
    |
1   | use std::io::Read;
    |

For more information about this error, try `rustc --explain E0599`.
error: could not compile `read-json-in-rust` due to previous error
```

Ok, we got an error: no method `read_to_string` found for struct `File`

Hm, but later it says that the method is available for File in the **_trait_** `std::io::Read`. A trait in rust is an interface type, and, as the compiler suggest, a trait must be in scope to able to use it.

So let bring it in scope by adding `use std::io::Read`.

```bash
> cargo run
   Compiling read-json-in-rust v0.1.0 (.../read-json-in-rust)
warning: unused variable: `data_source`
 --> src/main.rs:6:9
  |
6 |     let data_source = load_from_file("data/skbl.json");
  |         ^^^^^^^^^^^ help: if this is intentional, prefix it with an underscore: `_data_source`
  |
  = note: `#[warn(unused_variables)]` on by default

warning: `read-json-in-rust` (bin "read-json-in-rust") generated 1 warning (run `cargo fix --bin "read-json-in-rust"` to apply 1 suggestion)
    Finished dev [unoptimized + debuginfo] target(s) in 0.28s
     Running `target/debug/read-json-in-rust`
```

And, now it works!

## Dump JSON

Next up is to write the json to a new file, we add these lines to our main:

```rust
    let updated_data = data_source;
    dump_to_file(&updated_data, "data/skbl2.json");
```

And add this function:
```rust
fn dump_to_file(value: &Value, path: &str) {
    let writer = BufWriter::new(File::create(path).expect("failed to create file"));
    serde_json::to_writer(writer, value).expect("failed to serialize json")
}
```

1. We take value and path by reference (borrows them).
2. We create a file for writing with `File::create`, and panic on errors.
3. That file is unbuffered, so we add a `BufWriter` around the file to buffer the writes.
4. We serialize the `value` with serde_json.

After a successful `cargo run` we can look at our files:
```bash
> ls -l data
.rw-r--r-- 17M kristoffer  2 maj 14:36  skbl.json
.rw-r--r-- 16M kristoffer  2 maj 15:14  skbl2.json
```

Ok, we created the file, but it is smaller, why is that?

Inspections gives that `skbl.json` is written with ascii and `skbl2.json` uses utf-8.
