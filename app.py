# We now need the json library so we can load and export json data  
from flask import Flask, request,jsonify
import pandas as pd
import json
import numpy as np
import pickle
from datetime import datetime, timedelta
app = Flask(__name__)


@app.route('/')
def index():
    return 'API is working'

def read_transaction_table(ticker, date):
    # I should read this table with the transaction information
    # from the table in the database. But this time, I going to read 
    # the information from the .csv file.
    df = pd.read_csv('denormalized_data.csv')
    # if we had the database system in sql the line code for connect to the
    # database should be
    # df = pandas.read_sql(query, conection_information)
    # filtering by ticker
    df_ticker = df[df['symbol'] == ticker]
    
    df_ticker['date'] = df_ticker['date'].apply(
            lambda x: datetime.strptime(x, '%Y-%m-%d'))
    df_ticker = df_ticker[df_ticker['date'] <= date]
    
    return df_ticker




    

@app.route('/signal', methods=['POST'])
def signal():
    # BASIC AUTH
    # this time I have put the password in plain text.
    # But these can be saved as environment variables as good practice
    # or query a record in a database with encrypted passwords with encrypted passwords
    if (request.authorization["username"] == 'cristobal_quezada') & (request.authorization["password"] == 'ria'):
        data = request.get_json()
        print(data)
        print('ejecutando prediccion')
        # conecction to database filtering by ticker
        #ticker = 'AAPL'
        ticker = data['ticker']
        #date = '2021-10-08'
        date = data['date']
        date = datetime.strptime(date, '%Y-%m-%d')
        table = read_transaction_table(ticker, date)

        table = table.sort_values(by=['date'])
        # calculate moving average
        table['MA_close'] = table['Adj Close'].rolling(50, min_periods=10).apply(lambda x: np.mean(x))
        table = table.sort_values(by=['date'], ascending=False)
        # 1 if 'close' is higher than 'MA'
        table['close_condition'] = table.apply(
            lambda x: 1 if x['Adj Close']> x['MA_close'] else 0, axis=1)
        
        table['signal'] = 'no_signal'
        
        
        
        table = table.sort_values(by=['date'])
        table = table.reset_index(drop=True)
        for i in range(10,len(table)):
            # we are gonna start with sell signal
            close_condition = table['close_condition'].iloc[i]
            signal = table['signal'].iloc[i]
 
            date_row = table['date'].iloc[i]
            date_row_past_days = date_row - timedelta(days=10)
            indice = max(0, i-10)
            date_row_past_market_days = table['date'][indice:i].max()
            # close > 50 day moving average
            if close_condition == 1:
                # check is no sell signal generated for the past 10 days
                # the generated a buy signal
                table_filter = table[(table['date']>=date_row_past_days) & (table['date']<=date_row)]
                # count past 10 days
                count1 = table_filter['signal'].value_counts()
                table_filter_10_market = table[(table['date']>=date_row_past_market_days) & (table['date']<=date_row)]
                # count last 10 market days
                count2 = table_filter_10_market['signal'].value_counts()
                try:
                    count_sell = count1['sell']
                except KeyError:
                    count_sell = 0
                    
                try:
                    count_sell_market = count2['sell']
                except KeyError:
                    count_sell_market = 0

                if (count_sell == 0) & (count_sell_market == 0):
                    table['signal'].iloc[i] = 'buy'
            
            # close_condtion = 0
            else:
                # Check is there is no buy singnal generated for the past 10 days, then generate
                # then generate a sell signal
                # if there wasa a buy signal generate for the past 10 stock market days, then do not
                # generate a sell signal
                table_filter = table[(table['date']>=date_row_past_days) & (table['date']<=date_row)]
                # count past 10 days
                count1 = table_filter['signal'].value_counts()
                table_filter_10_market = table[(table['date']>=date_row_past_market_days) & (table['date']<=date_row)]
                # count past 10 market days
                count2 = table_filter_10_market['signal'].value_counts()
                try:
                    count_buy = count1['buy']
                except KeyError:
                    count_buy = 0
                    
                    
                try:
                    count_buy_market = count2['buy']
                except KeyError:
                    count_buy_market = 0 
                    
                if (count_buy == 0) & (count_buy_market == 0):
                    table['signal'].iloc[i] = 'sell'
        # select date        
        output = table[table['date']==date]
        output_MA = output['MA_close'].iloc[0]
        output_signal = output['signal'].iloc[0]
        
        output_dict = {"50_moving_avg": output_MA,
                       "Signal": output_signal,
                       "response":200}
            
        return jsonify(output_dict)
                    
                    
                        
            
                    
                    
                
                
                
                
            
        
            
            
        
        
        
        #f = open('datos_prueba.json',)
     
        # returns JSON object as
        # a dictionary
        #df_data = pd.DataFrame(data)
        #print(df_data)

        #output = jsonify(prediction)
        output = 'Que pasa'
    
    else:
        output = 'Wrong username or password'
    # 
    return output

           

if __name__ == '__main__':
    print('Executing api')
    app.run(debug=True, host='0.0.0.0')
    
    
    
    
