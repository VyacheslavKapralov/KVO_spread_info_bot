from datetime import datetime

import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io

from loguru import logger
from settings import PARAMETERS


@logger.catch()
async def add_plot_spread(data_frame: pd.DataFrame, ticker: str):
    ap_lower = mpf.make_addplot(data_frame[f"BBL_{PARAMETERS['bollinger_period']}_{PARAMETERS['bollinger_deviation']}"],
                                panel=0, color='g', title='Lower Band')
    ap_middle = mpf.make_addplot(data_frame[f"BBM_{PARAMETERS['bollinger_period']}_{PARAMETERS['bollinger_deviation']}"],
                                 panel=0, color='y', title='Middle Band')
    ap_upper = mpf.make_addplot(data_frame[f"BBU_{PARAMETERS['bollinger_period']}_{PARAMETERS['bollinger_deviation']}"],
                                panel=0, color='r', title='Upper Band')

    fig, _ = mpf.plot(data_frame, type='line', addplot=[ap_lower, ap_middle, ap_upper], volume=False,
                      title=f"{ticker} с Bollinger Bands",
                      style='yahoo',
                      figscale=2,
                      tight_layout=True,
                      returnfig=True,
                      # datetime_format='%d %m %H:%M',
                      figratio=(16, 9),
                      )
    ax = fig.axes[0]
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=565))
    now_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    fig.savefig(f"data_base/plots/plot_BB_{now_datetime}", dpi=600, bbox_inches='tight')
    # mpf.show()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return buf


if __name__ == '__main__':
    logger.info('Running spread_chart.py from module utils')
