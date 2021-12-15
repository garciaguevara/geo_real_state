import mortgage
import datetime
import matplotlib.pyplot as plt
import numpy as np

def plot_interest_diff_periods(loan_amount, interest_rate, insurance_per_month, years_r, start_date):
    t_ins_l = []; t_years_l = []; t_interest_l = []; t_credit_l = []; month_pay_l=[]; month_pay_ci_l=[]
    for c_year in years_r:
        # for c_months in c_months_l:
        c_months = c_year * 12
        m = mortgage.Mortgage(interest=interest_rate, amount=loan_amount, months=c_months, start_date=start_date)
        total_insurance = insurance_per_month * c_months;
        t_ins_l.append(total_insurance / 1000.0)
        t_years_l.append(m.loan_years())
        total_interest = m.total_payout() - m.amount()
        t_interest_l.append(float(total_interest) / 1000.0)

        t_credit_l.append(float(total_interest + total_insurance) / 1000.0)
        month_pay_ci_l.append(m.monthly_payment() + insurance_per_month)
        month_pay_l.append(m.monthly_payment())

    xAxis = [x for x in range(len(t_ins_l))]
    fig = plt.figure(figsize=(11.0, 5.0));
    ax = fig.add_subplot(111);
    _ = plt.xticks(xAxis, t_years_l, rotation='vertical');
    plt.show()  # [x[0][8:13] for x in t_years_l]

    # ax.plot(xAxis, t_interest_l, 'o-', label="Total interest");  # "{} Max".format(metric) # listMinMetric=[x[2] for x in metricPerFile]
    # ax.plot(xAxis,t_credit_l,'cx-', label="Total credit")
    width = 0.2
    ax.bar(xAxis, t_interest_l, width, label='Total interest'); ax.set_ylim([0, 50]) # , yerr=men_std, ,vmax=40
    ax.bar(xAxis, t_ins_l, width, bottom=t_interest_l, label='Total insurance')  # yerr=women_std,
    ax.set_yticks(np.arange(0, 40, 1), minor=True); ax.grid(which='minor', color='b', linestyle='--', linewidth=0.3)
    ax.set_yticks(np.arange(0, 40, 5)); ax.grid(which='major', color='b', linestyle='-', linewidth=0.8)


    ax2 = ax.twinx()
    ax2.plot(xAxis, month_pay_l, 'r^-', label="Monthly pay");   ax2.set_ylim([600, 1600])# , vmax=1600
    ax2.set_yticks(np.arange(600, 1700, 100));
    ax2.grid(which='major', color='r', linestyle='-', linewidth=0.7)

    ax.set_xlabel(r"Years")
    ax.set_ylabel(r"Total payment k$");
    ax.legend(fontsize="small", loc=6)
    ax2.set_ylabel(r"Monthly pay $");
    ax2.legend(fontsize="small", loc=5);
    # plt.grid();
    fig.suptitle("{:.1f}k\$ loan with {:.2f}% interest and insurance {:.0f}\$/month".format(loan_amount/1000.0, interest_rate*100.0, insurance_per_month))

    # mortgage.print_summary(m)
    # m.payment_schedule_df()



#  https://www.meilleurtaux.com/credit-immobilier/simulation-de-pret-immobilier/calcul-des-mensualites.html

start_date = datetime.datetime.strptime('2022-05-01', '%Y-%m-%d')
years_r = range(10,25) ;# c_months_l=[120,180,240]


# loan_amount = 180000; interest_rate = 0.011

plot_interest_diff_periods(174500, 0.011, 50, years_r, start_date)

plot_interest_diff_periods(174500, 0.011, 30, years_r, start_date)
# loan_amount = 115000; interest_rate = 0.028




print("Adios")
# mortgage.print_summary(m)
# m.payment_schedule_df()

