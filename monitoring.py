"""
example performance monitoring script
"""

import re
import joblib
from dateutil.relativedelta import relativedelta
import os
import numpy as np
from fbprophet import Prophet
from sklearn.pipeline import Pipeline
from scipy.stats import wasserstein_distance
from countries import Countries
import pandas as pd


MONITORING_DIR = "monitoring"
MODEL_VERSION = 0.1
MODEL_VERSION_NOTE = "model for time-series"


def get_latest_trained_data(data_dir):
    """
    load the data used in the latest training
    """
    # fetch time-series formatted data

    model_name = re.sub("\.", "_", str(MODEL_VERSION))
    all_data = {}
    for country in Countries.names:

        data_file = os.path.join(data_dir, "latest-train-{}-{}.joblib".format(country, model_name))

        if not os.path.exists(data_file):
            raise Exception("cannot find {}-- did you train the model?".format(data_file))

        data = joblib.load(data_file)
        all_data[country] = data

    return all_data


def get_monitoring_tools(df):
    """
    determine outlier and distance thresholds
    return thresholds, outlier model(s) and source distributions for distances
    NOTE: for classification the outlier detection on y is not needed

    """

    y = df['y']

    model = Prophet()
    model.fit(df)

    last_date = pd.to_datetime(max(df['ds'].values)).date()

    target_date = last_date + relativedelta(days=30)

    date_range = pd.date_range(last_date, target_date, freq="D")

    future = pd.DataFrame({"ds": date_range})

    # forecast = model.predict(future)
    #
    #     y_pred = forecast[forecast['ds'] == target_date.strftime("%Y-%m-%d")]['yhat'].values[0]

    bs_samples = 1000
    wasserstein_y = np.zeros(bs_samples)

    for b in range(bs_samples):
        n_samples = int(np.round(0.80 * df.shape[0]))
        subset_indices = np.random.choice(np.arange(df.shape[0]), n_samples, replace=True).astype(int)
        y_bs = df[['y']].iloc[subset_indices]

        wasserstein_y[b] = wasserstein_distance(y.values, y_bs.values.squeeze())

    # determine thresholds as a function of the confidence intervals
    wasserstein_y.sort()
    wasserstein_y_threshold = wasserstein_y[int(0.975*bs_samples)] + wasserstein_y[int(0.025*bs_samples)]

    to_return = {"wasserstein_y":np.round(wasserstein_y_threshold,2),
                 "clf": "Prophet",
                 "latest_X":df['ds'],
                 "latest_y":y}
    return to_return


if __name__ == "__main__":

    # get latest training data
    all_data = get_latest_trained_data(MONITORING_DIR)

    # get performance monitoring tools
    for country in Countries.names:
        df = all_data[country]

        pm_tools = get_monitoring_tools(df['data'])

        print(f"\n\n {country}")
        print("wasserstein_y", pm_tools['wasserstein_y'])
        print("model", pm_tools['clf'])
        print("latest_X", pm_tools['latest_X'])
        print("latest_y", pm_tools['latest_y'])

print("done")