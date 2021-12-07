import logging
import os
import sys

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import ticker


class Reporter:
    def __init__(self):
        self.logger = logging.getLogger("SystemLogger")
        matplotlib.rcParams['font.family'] = 'Malgun Gothic'
        plt.style.use('seaborn-pastel')
        plt.xlabel('날짜')
        plt.ylabel('자산총액')
        plt.xticks(rotation='vertical')

    def make_daily_report(self):
        report_txt = "daily_report.txt"
        if not os.path.isfile(f'{sys.path[1]}/{report_txt}'):
            if not os.path.isfile(report_txt):
                self.logger.error(f'{sys.path[1]}/{report_txt} 파일이 없습니다.')
                return None
            else:
                f = open(report_txt, 'r')
        else:
            f = open(f'{sys.path[1]}/{report_txt}', 'r', encoding="UTF-8")
        daily_log_list = [(day_log.split(",")[0], int(day_log.split(",")[1])) for day_log in f.read().splitlines()]
        dailys = list(map(list, zip(*daily_log_list)))

        fig, ax = plt.subplots(figsize=(14, 7))
        ax.plot(dailys[0], dailys[1], marker='o', markersize=5)
        ax = plt.gca()
        ax.yaxis.set_major_locator(ticker.MultipleLocator(100000))

        first_day = dailys[0][0]
        last_day = dailys[0][-1]
        plt.title(f"{first_day[:4]}-{first_day[4:6]}-{first_day[6:]} ▶ "
                  f"{last_day[:4]}-{last_day[4:6]}-{last_day[6:]} 자산추이")
        plt.ticklabel_format(axis='y', style='plain')
        plt.tick_params(axis='y', length=10)
        plt.tick_params(axis='x', rotation=90)
        plt.grid(True, axis='y', color='gray', alpha=0.5, linestyle='--')
        plt.tick_params(axis='both', direction='in')
        plt.rcParams['xtick.major.size'] = 10000
        plt.show()


if __name__ == "__main__":
    # mylist = [["20211206", 123124], ["20211207", 456324], ["20211208", 967975]]
    # print(list(zip(*mylist)))
    # print(list(map(list, zip(*mylist))))
    reporter = Reporter()
    reporter.make_daily_report()
