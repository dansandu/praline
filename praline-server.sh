export FLASK_APP=praline.server
export FLASK_ENV=development
export PYTHONPATH=$(pwd)/sources
python3.9 -m flask run
