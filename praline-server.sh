$(dirname "$0")/test.sh
export FLASK_APP=praline.server
export FLASK_DEBUG
export PYTHONPATH=$(pwd)/sources
python3 -m flask run
