import logging
import os
import sys
from datetime import datetime

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import ticker

from util.SystemValue import root_path


class Reporter:
    def __init__(self):
        self.logger = logging.getLogger("SystemLogger")
        matplotlib.rcParams['font.family'] = 'Malgun Gothic'

    def get_report_txt_file(self, mode):
        report_txt = "daily_report.txt"
        if not os.path.isfile(f'{root_path()}/{report_txt}'):
            self.logger.error(f'{root_path()}/{report_txt} 파일이 없습니다.')
            return None
        return open(f'{root_path()}/{report_txt}', mode, encoding="UTF-8")

    def add_report_data(self, date: str, asset: int):
        daily_log_list = self.read_daily_log_list()
        dailys = list(map(list, zip(*daily_log_list)))
        if date in dailys[0]:
            return
        f = self.get_report_txt_file("a")
        f.write(f'{date},{asset}\n')
        f.close()

    def make_daily_report(self) -> str:
        daily_log_list = self.read_daily_log_list()

        dailys = list(map(list, zip(*daily_log_list)))
        fig, ax = plt.subplots(figsize=(14, 7))
        ax.plot(dailys[0], dailys[1], marker='o', markersize=5)
        ax = plt.gca()
        # ax.yaxis.set_major_locator(ticker.MultipleLocator(1000000))

        first_day = dailys[0][0]
        last_day = dailys[0][-1]
        filename = f'{root_path()}/daily_report/{first_day}-{last_day}.png'

        plt.style.use('seaborn-pastel')
        plt.xlabel('날짜')
        plt.ylabel('자산총액')
        plt.xticks(rotation='vertical')
        plt.title(f"{first_day[:4]}-{first_day[4:6]}-{first_day[6:]} ▶ "
                  f"{last_day[:4]}-{last_day[4:6]}-{last_day[6:]} 자산추이")
        plt.ticklabel_format(axis='y', style='plain')
        plt.tick_params(axis='y', length=10)
        plt.tick_params(axis='x', rotation=90)
        plt.grid(True, axis='y', color='gray', alpha=0.5, linestyle='--')
        plt.tick_params(axis='both', direction='in')
        plt.savefig(filename, dpi=200)
        plt.show()

        return filename

    def read_daily_log_list(self):
        f = self.get_report_txt_file("r")
        daily_log_list = [(day_log.split(",")[0], int(day_log.split(",")[1]))
                          for day_log
                          in f.read().splitlines()]
        f.close()
        return daily_log_list


if __name__ == "__main__":
    # mylist = [["20211206", 123124], ["20211207", 456324], ["20211208", 967975]]
    # print(list(zip(*mylist)))
    # print(list(map(list, zip(*mylist))))
    reporter = Reporter()
    # reporter.add_report_data("20211208", 5000000
    for _ in range(5):
        reporter.make_daily_report()
