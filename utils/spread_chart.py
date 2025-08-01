import os
from datetime import datetime

import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io

from loguru import logger


async def add_plot_spread(data_frame: pd.DataFrame, ticker: str):
    ap_lower = mpf.make_addplot(data_frame["BBL"], panel=0, color='g', title='Lower Band', secondary_y=False)
    ap_middle = mpf.make_addplot(data_frame["BBM"], panel=0, color='y', title='Middle Band', secondary_y=False)
    ap_upper = mpf.make_addplot(data_frame["BBU"], panel=0, color='r', title='Upper Band', secondary_y=False)
    fig, axlist = mpf.plot(
        data_frame,
        type='line',
        addplot=[ap_lower, ap_middle, ap_upper],
        volume=False,
        title=f"{ticker} with Bollinger Bands",
        style='yahoo',
        figscale=2,
        tight_layout=True,
        returnfig=True,
        figratio=(16, 9),
    )
    ax = axlist[0]
    # ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=485))
    now_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    db_path = 'database/plots'
    os.makedirs(db_path, exist_ok=True)
    fig.savefig(f"{db_path}/{now_datetime}", dpi=600, bbox_inches='tight')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return buf


if __name__ == '__main__':
    logger.info('Running spread_chart.py from module utils')
