import datetime as dt

import pandas as pd
import pyarrow.parquet as pq

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Select, HoverTool, MultiChoice
from bokeh.models import NumeralTickFormatter, Div, BoxAnnotation
from bokeh.plotting import figure

#################################################################################
# This just loads in the data...
# Alot of this was built off this "cross-fire demo"
# https://github.com/bokeh/bokeh/blob/branch-2.3/examples/app/crossfilter/main.py

final_month = 1
final_year = 2026

background = "#ffffff"

file = "./data"+ "/tri-all-country-data.parquet"

df = pq.read_table(file).to_pandas()

# Set date as index and prepare for multi-select
df.set_index(['CTY_NAME', 'date'], inplace=True)

country_options = df.index.get_level_values('CTY_NAME').unique().to_list()

# Default selections
country = ["ALL COUNTRIES", "CANADA"]
metric = "TRI Tariff"

#################################################################################
# No functions needed for TRI data - it's already calculated


#################################################################################
# Then this makes the simple plots:

def make_plot():
    
    height = int(1.15*533)
    width = int(1.15*750)
    
    # Map metric selection to column name
    metric_map = {
        'TRI Tariff': 'sqrtariff',
        'Weighted Mean Tariff': 'meanweighted',
        'Duty / Imports Tariff': 'simplemean',
        'Statutory Tariff': 'effective tariff',
        'Total Duties': 'duty_total'
    }
    
    metric_column = metric_map[metric_select.value]
    is_dollar_metric = (metric_select.value == 'Total Duties')
    
    # Build title
    title_name = ""
    for name in country_select.value:
        if len(country_select.value) <= 2:
            title_name = title_name + name + ", "
        if len(country_select.value) > 2:
            title_name = title_name + name[0:3] + ", "
        
    title = metric_select.value + " for " + title_name.rstrip(", ")

    plot = figure(x_axis_type="datetime", height=height, width=width, toolbar_location = 'below',
           tools = "box_zoom, reset, pan, xwheel_zoom", title = title,
                  x_range = (dt.datetime(2024,9,1),dt.datetime(final_year,final_month,1)) )
    
    # Get fixed colors from the dataframe for each selected country
    line_colors = []
    line_widths = []
    
    for country_name in country_select.value:
        country_color = df.loc[country_name].iloc[0]['color']
        line_colors.append(country_color)
        line_widths.append(6)
    
    # Plot each country as a separate line for legend support
    for i, country_name in enumerate(country_select.value):
        country_data = df.loc[country_name].sort_index()
        
        # Convert to percentage for tariff rates, keep as-is for dollar amounts
        y_values = country_data[metric_column].values if is_dollar_metric else 100 * country_data[metric_column].values
        
        # Create ColumnDataSource with flag URL
        source = ColumnDataSource(data=dict(
            x=country_data.index,
            y=y_values,
            country=[country_name] * len(country_data),
            flag=[country_data['flag'].iloc[0]] * len(country_data)
        ))
        
        plot.line('x', 'y', source=source,
                 line_width=line_widths[i], line_alpha=0.75, line_color=line_colors[i],
                 legend_label=country_name, name=country_name)
        
    # fixed attributes
    plot.xaxis.axis_label = None
    plot.yaxis.axis_label = "Total Duties (USD)" if is_dollar_metric else "Tariff Rate (%)"
    plot.axis.axis_label_text_font_style = "bold"
    plot.axis.axis_label_text_font_size = "16pt"
    plot.grid.grid_line_alpha = 0.3
    
    if is_dollar_metric:
        TIMETOOLTIPS = """
                <div style="background-color:#F5F5F5; opacity: 0.95; border: 5px 5px 5px 5px;">
                <div style = "text-align:left;">
                <span style="font-size: 13px; font-weight: bold">
                <img src="@flag" alt="" style="height:20px; vertical-align:middle; margin-right:8px;"> @country
                 </span>
                 </div>
                 <div style = "text-align:left;">
                <span style="font-size: 13px; font-weight: bold"> @x{%b %Y}:  @y{$0.0a}</span>   
                </div>
                </div>
                """
    else:
        TIMETOOLTIPS = """
                <div style="background-color:#F5F5F5; opacity: 0.95; border: 5px 5px 5px 5px;">
                <div style = "text-align:left;">
                <span style="font-size: 13px; font-weight: bold">
                <img src="@flag" alt="" style="height:20px; vertical-align:middle; margin-right:8px;"> @country
                 </span>
                 </div>
                 <div style = "text-align:left;">
                <span style="font-size: 13px; font-weight: bold"> @x{%b %Y}:  @y{0.1f}%</span>   
                </div>
                </div>
                """
        
    plot.add_tools(HoverTool(tooltips = TIMETOOLTIPS,  line_policy='nearest', formatters={'@x': 'datetime'}))
    
    # Configure legend
    plot.legend.location = "top_left"
    plot.legend.click_policy = "hide"  # Click to hide/show lines
    plot.legend.label_text_font_size = "10pt"
    plot.legend.spacing = 2
    plot.legend.padding = 5
    
    plot.title.text_font_size = '13pt'
    plot.background_fill_color = background 
    plot.background_fill_alpha = 0.75
    plot.border_fill_color = background 
    
    trump2_box = BoxAnnotation(left=dt.datetime(2025,4,2), right=dt.datetime(final_year,final_month,1), fill_color='red', fill_alpha=0.1)
    plot.add_layout(trump2_box)
    
    # Make tick labels bold and larger
    plot.xaxis.major_label_text_font_style = "bold"
    plot.xaxis.major_label_text_font_size = "12pt"
    plot.xaxis.major_label_orientation = 0.785  # 45 degrees in radians (pi/4)
    plot.yaxis.major_label_text_font_style = "bold"
    plot.yaxis.major_label_text_font_size = "12pt"
    
    plot.sizing_mode= "scale_both"
    
    # Format y-axis as dollars or percentages based on metric
    if is_dollar_metric:
        plot.yaxis.formatter = NumeralTickFormatter(format="($0.0a)")
    else:
        plot.yaxis.formatter = NumeralTickFormatter(format="(0.0)")
    
    plot.max_height = height
    plot.max_width = width
    
    plot.min_height = int(0.25*height)
    plot.min_width = int(0.25*width)
    
    return plot

#################################################################################

def update_plot(attrname, old, new):
    layout.children[0] = make_plot()

#################################################################################

country_select = MultiChoice(value=country, title='Country', options=sorted(country_options), width=325)
country_select.on_change('value', update_plot)
                        
#################################################################################

metric_select = Select(value=metric, title='Tariff Metric', options=['TRI Tariff', 'Weighted Mean Tariff', 'Duty / Imports Tariff', 
                                                                     'Statutory Tariff', 'Total Duties'], width=350)
metric_select.on_change('value', update_plot)

#################################################################################

div0 = Div(text = """<b>TRI Tariff</b>: Trade Restrictiveness Index.<br>
    <b>Weighted Mean</b>: 2024 Import-weighted average tariff.<br>
    <b>Duty / Imports</b>: Total duties divided by total imports.<br>
    <b>Total Duties</b>: Total customs duties collected in USD.\n
    """, width=350, background = background, styles={"justify-content": "space-between", "display": "flex"} )

div1 = Div(text = """Select one or more countries to compare. Data covers top 20 U.S. trading partners plus ALL COUNTRIES aggregate.\n
    """, width=350, background = background, styles={"justify-content": "space-between", "display": "flex"} )

controls = column(country_select, div1, metric_select, div0)

height = int(1.95*533)
width = int(1.95*675)

layout = row(make_plot(), controls, sizing_mode = "scale_height", max_height = height, max_width = width,
              min_height = int(0.25*height), min_width = int(0.25*width))

curdoc().add_root(layout)
curdoc().title = "US Trade Restrictiveness Index Tracker"
