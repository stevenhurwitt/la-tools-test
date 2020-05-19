# LA-tools

Contains Python tools for Load Analytics department - Engie, NA.

[![Binder](https://mybinder.org/badge_logo.svg)](https://la-tools-engie.southcentralus.cloudapp.azure.com/hub/user-redirect/git-pull?repo=https%3A%2F%2Fgithub.com%2Fstevenhurwitt%2Fla-tools-test&app=notebook)


## 1. .json to .csv Parser
Found in [this file in the main directory](/user/engiela/notebooks/la-tools-test/EWX_Forecast/Forecasts-JSONtoCSV.ipynb).

Parses EWX .json files and outputs forecasts to .csv (can be used if EWX forecasts aren't coming through to ALPS).

**To Do** Add functionality to parse payloads we send to EWX (can be used for tickets, to recover data, etc.).
Add functionality to check heartbeat (time difference) of forecasts.

## 2. EWX Forecasting Default IDR Flow
Found in [EWX Forecasting Directory](/user/engiela/notebooks/la-tools-test/EWX_Forecast/EWX_Forecast_Main.ipynb)

Attempts to replicate EWX Forecasting default flow configs. Workaround timeshift for a year of IDR data.

## 3. IDR Drop
Found in [IDR_Drop Directory](/user/engiela/notebooks/la-tools-test/IDR_Drop)

1. [Email scrape tool](/user/engiela/notebooks/la-tools-test/IDR_Drop/emailscrape.py) - Parses utility emails for accounts, EPO logins and passwords.
2. [EPO webscrape tool](/user/engiela/notebooks/la-tools-test/IDR_Drop/IDR_Drop_Portal.ipynb) - Automates downloading of IDR data from EPO portal.
3. [IDR filter](/user/engiela/notebooks/la-tools-test/IDR_Drop/IDR_Drop.ipynb) - splits IDR data into Raw IDR files, filters raw IDR into ch. 1 and/or ch. 3 to be dropped into ALPS.
4. [Main code](/user/engiela/notebooks/la-tools-test/IDR_Drop/Van_Pham_IDR_Drop.py) - puts everything together, to be automated.
