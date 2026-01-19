# TRI-tracker

An interactive Bokeh server application to visualize U.S. tariffs and Trade Restrictiveness Indexes over time.

## Overview

This application provides an interactive dashboard for tracking and analyzing various tariff metrics for the top 20 U.S. trading partners. It allows users to compare multiple countries, explore different tariff measures, and download both visualizations and data.

## Features

- **Interactive Time-Series Visualization**: View tariff trends from September 2024 to January 2026
- **Multiple Tariff Metrics**:
  - **TRI Tariff**: Trade Restrictiveness Index (square root tariff)
  - **Weighted Mean Tariff**: 2024 import-weighted average tariff
  - **Duty / Imports Tariff**: Total duties divided by total imports
  - **Statutory Tariff**: Announced tariffs, 2024 import-weighted
  - **Total Duties**: Total customs duties collected (in USD)
- **Multi-Country Comparison**: Select and compare multiple countries simultaneously
- **Visual Indicators**: Red shaded region highlights policy periods (Trump 2 administration from April 2025)
- **Interactive Tools**: Zoom, pan, and hover for detailed information with country flags
- **Export Capabilities**:
  - Download charts as PNG using the toolbar save button
  - Export selected data as CSV with a generated download link

## Data Source

The tariff data used in this application is sourced from the **Trade War Tracker** project:

**Repository**: [https://github.com/tradewartracker/how-restrictive-us-trade](https://github.com/tradewartracker/how-restrictive-us-trade)

The data is stored in Parquet format at `data/tri-all-country-data.parquet` and includes historical tariff information for the top 20 U.S. trading partners plus an "ALL COUNTRIES" aggregate.

## Technology Stack

- **Bokeh 3.3.4**: Interactive visualization framework
- **Pandas 2.1.4**: Data manipulation and analysis
- **PyArrow 14.0.2**: Parquet file handling
- **NumPy 1.26.3**: Numerical computations
- **Python 3.11**: Runtime environment

## Deployment

This application is deployed on **Heroku** as a web dyno running a Bokeh server.

### Deployment Configuration

**Procfile**:
```
web: bokeh serve --port=$PORT --allow-websocket-origin=tri-tracker-d17ad5511b2b.herokuapp.com --address=0.0.0.0 --use-xheaders main-tri-tracker.py
```

**Key deployment settings**:
- Uses Heroku's dynamic `$PORT` environment variable
- Configured for WebSocket connections from the Heroku domain
- Uses `--address=0.0.0.0` for proper routing through Heroku's infrastructure
- Includes `--use-xheaders` to handle Heroku's proxy headers correctly

### Deploying to Heroku

1. **Prerequisites**:
   - Heroku CLI installed
   - Git repository initialized
   - Heroku account created

2. **Create Heroku app**:
   ```bash
   heroku create tri-tracker
   ```

3. **Configure Python buildpack**:
   ```bash
   heroku buildpacks:set heroku/python
   ```

4. **Deploy**:
   ```bash
   git add .
   git commit -m "Deploy TRI tracker"
   git push heroku main
   ```

5. **Open the application**:
   ```bash
   heroku open
   ```

The app will be available at: `https://tri-tracker-d17ad5511b2b.herokuapp.com/main-tri-tracker`

## Local Development

To run the application locally:

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Bokeh server**:
   ```bash
   bokeh serve --show main-tri-tracker.py
   ```

3. **Access the application**:
   Open your browser to `http://localhost:5006/main-tri-tracker`

## File Structure

```
TRI-tracker/
├── main-tri-tracker.py    # Main Bokeh application
├── Procfile               # Heroku deployment configuration
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── LICENSE               # License information
└── data/
    └── tri-all-country-data.parquet  # Tariff data (Parquet format)
```

## Usage

1. **Select Countries**: Use the multi-select dropdown to choose one or more countries to compare
2. **Choose Metric**: Select the tariff metric you want to visualize
3. **Interact with Chart**: 
   - Hover over lines to see detailed values with country flags
   - Click legend items to hide/show specific countries
   - Use toolbar to zoom, pan, or reset the view
4. **Download Chart**: Click the save icon (💾) in the chart toolbar
5. **Download Data**: Click "Generate CSV Download Link" button, then click the generated link to download CSV data

## Notes

- The application uses Bokeh 2.0.0 compatibility for local development (uses `styles` attribute)
- Production deployment on Heroku runs Bokeh 3.3.4
- Different metrics may have different date ranges depending on data availability
- CSV export only includes data points where values exist (no empty entries)

## License

See [LICENSE](LICENSE) file for details.
