import datetime as dt

import pandas as pd
import pyarrow.parquet as pq

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Select, HoverTool, MultiChoice
from bokeh.models import NumeralTickFormatter, Div, BoxAnnotation, Button
from bokeh.models import CustomJS
from bokeh.plotting import figure
import io
import base64

#################################################################################
# This just loads in the data...
# Alot of this was built off this "cross-fire demo"
# https://github.com/bokeh/bokeh/blob/branch-2.3/examples/app/crossfilter/main.py

final_month = 2
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
           tools = "box_zoom, reset, pan, xwheel_zoom, save", title = title,
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

def download_csv():
    """Generate CSV data for currently selected countries and metric"""
    metric_map = {
        'TRI Tariff': 'sqrtariff',
        'Weighted Mean Tariff': 'meanweighted',
        'Duty / Imports Tariff': 'simplemean',
        'Statutory Tariff': 'effective tariff',
        'Total Duties': 'duty_total'
    }
    
    metric_column = metric_map[metric_select.value]
    is_dollar_metric = (metric_select.value == 'Total Duties')
    
    # Collect data for all selected countries
    data_list = []
    for country_name in country_select.value:
        country_data = df.loc[country_name].sort_index()
        for idx, row in country_data.iterrows():
            value = row[metric_column]
            # Skip rows where the metric value is NaN or missing
            if pd.notna(value):
                display_value = value if is_dollar_metric else value * 100
                data_list.append({
                    'Country': country_name,
                    'Date': idx.strftime('%Y-%m-%d'),
                    'Metric': metric_select.value,
                    'Value': display_value
                })
    
    # Create DataFrame and export to CSV
    export_df = pd.DataFrame(data_list)
    csv_string = export_df.to_csv(index=False)
    
    # Create data URI for download link
    b64 = base64.b64encode(csv_string.encode()).decode()
    data_uri = f"data:text/csv;base64,{b64}"
    
    # Update the download link div
    download_link_div.text = f'''
    <a href="{data_uri}" download="tariff_data.csv" 
       style="display:inline-block; padding:10px 20px; background-color:#28a745; 
              color:white; text-decoration:none; border-radius:4px; font-weight:bold;">
       Click Here to Download CSV
    </a>
    '''

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

# Download CSV button and link
download_button = Button(label="Generate CSV Download Link", button_type="success", width=350)
download_button.on_click(download_csv)

download_link_div = Div(text="", width=350, height=50)

#################################################################################

div0 = Div(text = """<b>TRI Tariff</b>: Trade Restrictiveness Index.<br>
    <b>Weighted Mean</b>: 2024 Import-weighted average tariff.<br>
    <b>Duty / Imports</b>: Total duties divided by total imports.<br>
    <b>Statutory Tariff</b>: Announced tariffs, 2024 Import-weighted.<br>    
    <b>Total Duties</b>: Total customs duties collected in USD.\n
    """, width=350, background = background, styles={"justify-content": "space-between", "display": "flex"} )

div1 = Div(text = """Select one or more countries to compare. Data covers top 20 U.S. trading partners plus ALL COUNTRIES aggregate.\n
    """, width=350, background = background, styles={"justify-content": "space-between", "display": "flex"} )

div2 = Div(text = """<b>Download Chart:</b> Use the save icon (💾) in the chart toolbar to download as PNG.<br>
    <b>Download Data:</b> Click the button to generate a download link for CSV data.\n
    """, width=350, background = background, styles={"justify-content": "space-between", "display": "flex"} )

controls = column(country_select, div1, metric_select, div0, download_button, download_link_div, div2)

height = int(1.95*533)
width = int(1.95*675)

layout = row(make_plot(), controls, sizing_mode = "scale_height", max_height = height, max_width = width,
              min_height = int(0.25*height), min_width = int(0.25*width))

curdoc().add_root(layout)
curdoc().title = "US Trade Restrictiveness Index Tracker"
