## Praline

A simple C++ build tool and dependency manager. Requires Python 3.6 or later. For MacOS the Clang compiler is needed. For Windows and Linux the GCC compiler is required.

### Quick setup

Clone the repository to a desired directory and run the following commands inside the it:

    python3 -m pip install flask requests pyyaml
    ./praline-server.sh

This will install the required Python packages to run the application and start the package managing server. By default packages are stored in the `repository/packages` directory but you can change it in `resources/praline-server.config` .

### Building your first artifact

Create a directory named `hello_world` and inside it create a file named `Pralinefile` with the following contents:

    organization: foobar
    artifact: hello_world
    version: 1.0.0

Then open the terminal in the directory and run the following commands:

    export PATH=$PATH:<path to cloned repo>/sources
    praline.py --executable --skip-formatting run_main_executable

This adds the `praline.py` script to the path so you can easily invoke it from anywhere. The second command invokes the script and builds the project as an executable artifact by specifying the `--executable` flag. If you have `clang-format` in the environment path you can omit the `--skip-formatting` flag. Inside the terminal you should see something like this:

    2019-04-13 20:34:20,519 INFO praline.common.file_system Hello, world!

For more information visit the wiki page.
