SCRIPT_DIRECTORY=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

if [[ $# -eq 0 ]] then
    SCRIPT_BUILD_MODE="debug"
else
    SCRIPT_BUILD_MODE="$1"
fi

echo "Removing existing packages"

cd "$SCRIPT_DIRECTORY/.repository/packages"

rm -f *.tar.gz

cd "$SCRIPT_DIRECTORY/.."

build_project()
{
    echo "Building $1"
    cd $1 && praline.py clean && praline.py --mode="$SCRIPT_BUILD_MODE" deploy && praline.py clean && cd ..
    return $?
}

build_project journey &&
    build_project service_runner &&
    build_project radiance &&
    build_project ballotin &&
    build_project glyph &&
    build_project farseer
