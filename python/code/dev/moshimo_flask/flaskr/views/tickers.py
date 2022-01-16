from flask import Blueprint
from flaskr.models.tickers import Tickers

# set route
tickers = Blueprint('user_router', __name__)

@job.route('/<int:id>', methods=['GET'])
def gettickers(id):
    tickers = Tickers.searchBy(id)
    print(tickers)