import sys
from datetime import datetime
from verify import plot_met_avg_pre24

if __name__ == '__main__':
    model_name = sys.argv[1]
    report_time = datetime.strptime(sys.argv[2], "%Y%m%d%H")
    report_time2 = datetime.strptime(sys.argv[3], "%Y%m%d%H")
    cst = int(sys.argv[4])
    plot_met_avg_pre24.single_plot(model_name, report_time, report_time2, cst)
