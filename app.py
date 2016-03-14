import pandas as pd
from bokeh.models import  Callback, ColumnDataSource
from bokeh.plotting import figure, output_notebook, show
from bokeh.palettes import Spectral4
from bokeh.embed import components
from flask import Flask, flash, render_template, request, redirect, url_for
import requests
from wtforms import Form, StringField, BooleanField
from bokeh.models import HoverTool



def get_data(stock):
    api_url = 'https://www.quandl.com/api/v1/datasets/WIKI/%s.json' % stock
    session = requests.Session()
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
    raw_data = session.get(api_url)
    return raw_data.json()

def to_dataframe(json_data,days):
    df = pd.DataFrame(json_data['data'],columns=json_data['column_names'])
    df = df[:days]
    df = df.set_index('Date')
    df.index = pd.to_datetime(df.index)
    return df 

class stockForm(Form):
    stock = StringField('Ticker symbol')
    Closing = BooleanField('Closing price')
    Opening = BooleanField('Opening price')
    Adj_closing = BooleanField('Adjusted closing price')
    Adj_opening = BooleanField('Adjusted opening price')


app = Flask(__name__)

@app.route('/')
def main():
    return redirect('/index')

# Index page where user select stock to display
@app.route('/index',methods=['GET','POST'])
def index():
    form =  stockForm(request.form)
    if request.method=="GET":
    	return render_template('index.html',form=form)
    else:
        app.stockForm = form
        json_data = get_data(app.stockForm.data['stock'])
        app.json_data = json_data
        if 'error' in json_data:
        	return render_template('error.html')
        else:
        	return redirect('/graph')


@app.route('/error',methods=['GET','POST'])
def error():
    if request.method=="GET":
    	return render_template('error.html',form=form)
    else:
        return redirect('/index')

  
# Display Bokeh graph
@app.route('/graph')
def graph():
    df = to_dataframe(app.json_data,25)
    f=open('data.txt','w')
    f.write('%s\n'%(df))
    name_map = {'Closing':'Close',
                'Opening':'Open',
                'Adj_closing':'Adj. Close',
                'Adj_opening':'Adj. Open'}
    
    plot_set = [name_map[key] for key in app.stockForm.data.keys() if app.stockForm.data[key] == True]
    f.write('%s\n'%plot_set)
    f.close()
    
    #make color palette for the lines
    numlines=len(plot_set) 
    mypalette=Spectral4[0:numlines]
    
    p = figure(width=800, height=250, x_axis_label='date', x_axis_type="datetime",tools="pan ,wheel_zoom ,reset ,save,hover,tap")
    
    # plot lines
    
    hover = p.select(dict(type=HoverTool))
    hover.mode='mouse'
    
    if len(plot_set)==1:
    	hover.tooltips = [('Date', "@Date"),(plot_set[0],'@price1{0.00}')]
    	df_plot=ColumnDataSource({'index': df.index, 'price1': df[plot_set[0]], 'Date': df.index.format()})
    	p.line('index', 'price1', source=df_plot, line_color=mypalette[0], line_width=2, legend=plot_set[0])
    
    if len(plot_set)==2:
    	hover.tooltips = [('Date', "@Date"),(plot_set[0],'@price1{0.00}'),(plot_set[1],'@price2{0.00}')]
    	df_plot=ColumnDataSource({'index': df.index, 'price1': df[plot_set[0]],'price2': df[plot_set[1]], 'Date': df.index.format()})
    	for color_index,line_name in enumerate(plot_set):
        	p.line('index', 'price'+str(color_index+1), source=df_plot, line_color=mypalette[color_index], line_width=2, legend=line_name)
        	
    if len(plot_set)==3:
    	hover.tooltips = [('Date', "@Date"),(plot_set[0],'@price1{0.00}'),(plot_set[1],'@price2{0.00}'),(plot_set[2],'@price3{0.00}')]
    	df_plot=ColumnDataSource({'index': df.index, 'price1': df[plot_set[0]],'price2': df[plot_set[1]],'price3': df[plot_set[2]], 'Date': df.index.format()})
    	for color_index,line_name in enumerate(plot_set):
    		p.line('index', 'price'+str(color_index+1), source=df_plot, line_color=mypalette[color_index], line_width=2, legend=line_name)
    		
    if len(plot_set)==4:
    	hover.tooltips = [('Date', "@Date"),(plot_set[0],'@price1{0.00}'),(plot_set[1],'@price2{0.00}'),(plot_set[2],'@price3{0.00}'),(plot_set[3],'@price4{0.00}')]
    	df_plot=ColumnDataSource({'index': df.index, 'price1': df[plot_set[0]],'price2': df[plot_set[1]],'price3': df[plot_set[2]],'price4': df[plot_set[3]], 'Date': df.index.format()})
    	for color_index,line_name in enumerate(plot_set):
        	p.line('index', 'price'+str(color_index+1), source=df_plot, line_color=mypalette[color_index], line_width=2, legend=line_name)
        
    script, div = components(p)

    return render_template('graph.html', stock_name = app.stockForm.data['stock'], script=script, div=div)


if __name__ == '__main__':
    app.run(port=33507)
