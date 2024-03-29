# Praline
Simple C++ build tool and dependency manager. Requirements for different platforms:
- MacOS requires the Clang compiler
- Windows requires an installation of Microsoft Visual Studio
- Linux requires the GCC compiler

All platforms need Python 3.9 or later with the following packages. Run the command inside a terminal to install them:
```bash
python3.9 -m pip install flask requests pyyaml
```
## Quick setup
Clone the project to a desired directory and run the following command inside the directory:
```bash
./praline-server.sh
```
The command starts the Praline package manager server. By default, packages are stored inside the `repository/packages` directory but you can change it in the `resources/praline-server.config` file.
## Building your first artifact
Create a directory named `hello_world` and add a file named `Pralinefile` inside it with the following contents:
```yaml
organization: my_organization
artifact: hello_world
version: 1.0.0
```
Praline uses the file to build and manage artifacts for the project. Next, open the terminal in the directory and run the following commands:
```bash
export PATH=$PATH:<path to cloned repo>/sources
praline.py --artifact-type=executable --skip-formatting main
```
The first command adds the `praline.py` script to the path so you can easily invoke it inside the terminal. The second command invokes the script and builds the project as an executable artifact by specifying the `--artifact-type=executable` flag. You can omit the `--skip-formatting` flag if the `clang-format` executable path is set in the `resources/praline-client.config` file using the `clang-format-executable-path` key, or if the environment `PATH` variable contains the path to the executable. After running the command the terminal should print `Hello, world!`
