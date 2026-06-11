python -m pip install pytest

python -m pytest generate-password/handler_test.py -q -vv
python -m pytest generate-2fa/handler_test.py -q -vv
python -m pytest authenticate/handler_test.py -q -vv