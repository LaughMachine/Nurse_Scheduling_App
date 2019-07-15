#!/usr/bin/env python
from model import InputForm_staffing_AM, InputForm_staffing_PM, \
    InputForm_census_PM, InputForm_census_AM
from flask import Flask, render_template, request
from compute import heuristic_empty
from compute import two_part_heuristic_empty
from compute import three_class_heuristic_empty
from compute import round_standard
from scipy.optimize import curve_fit
from time import localtime, strftime
import numpy as np
import csv
import os

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("view_start.html")

@app.route('/shift_staffing', methods=['GET', 'POST'])
def shift_staffing():
    return render_template("view_shift.html",form=None)

@app.route('/shift_census', methods=['GET', 'POST'])
def shift_census():
    return render_template("view_census.html",form=None)

@app.route('/staffing_form_am', methods=['GET', 'POST'])
def staffing_form_AM():
    form = InputForm_staffing_AM(request.form)
    if request.method == 'POST' and form.validate():
        # Get data from form
        actual = [form.currnum1_0.data, form.currnum2_0.data, form.currnum3_0.data, form.currnum4_0.data]
        actual_edin = [form.currnum1_2_0.data, form.currnum2_2_0.data, form.currnum3_2_0.data]
        # Create data row
        row = [strftime("%Y-%m-%d %H:%M:%S", localtime()), form.dt.data,'AM'] + actual + actual_edin
        row.append(form.text.data)
        # Create storage file if it doesn't exist, otherewise write to file
        if not os.path.exists(os.getcwd()+'/staffing_data.csv'):
            with open('staffing_data.csv', 'w') as fil:
                r = csv.writer(fil)
                header = ['date_of_input', 'date', 'shift','bay_A_nurses','bay_B_nurses','bay_C_nurses',
                          'bay_U_nurses','bay_A_EDIN','bay_B_EDIN','bay_C_EDIN','notes']
                r.writerow(header)
                r.writerow(row)
        else:
            with open('staffing_data.csv', 'a') as fil:
                r = csv.writer(fil)
                r.writerow(row)
        # Get information of new page
        curr_page = 'view_return.html'
        curr_form = None
        result = None
    else:
        curr_page = 'shift_form_am.html'
        curr_form = form
        result = None

    return render_template(curr_page, form=curr_form, result=result)

@app.route('/staffing_form_pm', methods=['GET', 'POST'])
def staffing_form_PM():
    form = InputForm_staffing_PM(request.form)
    if request.method == 'POST' and form.validate():
        # Get data from form
        actual = [form.currnum1_0.data, form.currnum2_0.data, form.currnum3_0.data, 0]
        actual_edin = [form.currnum1_2_0.data, form.currnum2_2_0.data, form.currnum3_2_0.data]
        # Create data row
        row = [strftime("%Y-%m-%d %H:%M:%S", localtime()), form.dt.data, 'PM'] + actual + actual_edin
        row.append(form.text.data)
        # Create storage file if it doesn't exist, otherewise write to file
        if not os.path.exists(os.getcwd() + '/staffing_data.csv'):
            with open('staffing_data.csv', 'w') as fil:
                r = csv.writer(fil)
                header = ['date_of_input', 'date', 'shift', 'bay_A_nurses', 'bay_B_nurses', 'bay_C_nurses',
                          'bay_U_nurses','bay_A_EDIN', 'bay_B_EDIN', 'bay_C_EDIN','notes']
                r.writerow(header)
                r.writerow(row)
        else:
            with open('staffing_data.csv', 'a') as fil:
                r = csv.writer(fil)
                r.writerow(row)
        # Get information of new page
        curr_page = 'view_return.html'
        curr_form = None
        result = None
    else:
        curr_page = 'shift_form_pm.html'
        curr_form = form
        result = None

    return render_template(curr_page, form=curr_form, result=result)

@app.route('/census_form_am', methods=['GET', 'POST'])
def census_form_AM():
    form = InputForm_census_AM(request.form)
    if request.method == 'POST' and form.validate():
        # Load necessary data
        optA = [2.15417, -0.5621]
        optB = [2.2625, -0.7571]
        optC = [2.075, -0.5468]
        optU = [2.49025, -0.5141]
        p = [0.45, 0.36, 0.45]
        A_AM = [2.56, 2.73, 2.45]
        A_PM = [1.75, 1.79, 1.70]
        ded = [4.0 / 11.0, 3.0 / 11.0, 3.0 / 11.0, 1.0 / 11.0]
        g = [12.0, 12.0, 12.0, 10.0]
        b = [optA[1], optB[1], optC[1], optU[1]]
        if 3 < form.numnurse.data < 9:
            reserved_nurses = [1, 1, 1, 1]
        elif form.numnurse.data <= 3:
            reserved_nurses = [0, 0, 0, 0]
        else:
            reserved_nurses = [4, 2, 2, 1]
        # Get data from form
        nurses = form.nursetopat.data * form.numnurse.data          # Number of nurses
        n_to_pat = form.nursetopat_2.data                           # Nurse to patient ratio for EDIN
        ed_nurses = form.numnurse_2.data                            # EDIN nurses
        service_rates = [6.767, 6.033, 6.983, 1.733]                # Service Rates for patients
        w_mu = [1/s for s in service_rates]                         # Average service time
        norm_b = [x / float(nurses) for x in b]                     # Normed b value
        # Current number of patients waiting
        ex_pat = [form.currnum1.data, form.currnum2.data, form.currnum3.data, form.currnum4.data]
        x_bar = [x / float(nurses) for x in ex_pat]
        # Current number of inpatients
        in_pat = [form.currnum1_2.data, form.currnum2_2.data, form.currnum3_2.data]
        # Calculated inpatients for the period
        in_pat_tot = [x + p[ind] * (ex_pat[ind] + A_AM[ind]) for ind, x in enumerate(in_pat)]
        in_pat_load = [x / float(sum(in_pat_tot)) for x in in_pat_tot]
        # Divides EDIN nurses proportional to inpatients
        edin_alloc = round_standard(in_pat_load, ed_nurses)
        # Finds excess inpatients after allocating EDIN nurses
        excess_in_pat = []
        allocatable = form.numnurse.data - sum(reserved_nurses)
        extra_nurse_demand = 0
        for ind, x in enumerate(in_pat):
            excess_in_pat.append(np.ceil(max(x - n_to_pat * edin_alloc[ind], 0) /
                                         float(n_to_pat)))
            extra_nurse_demand += max(excess_in_pat[ind] - reserved_nurses[ind], 0)
        excess_in_pat.append(0)
        if extra_nurse_demand > allocatable:
            new_excess_in_pat = [max(x - reserved_nurses[ind], 0) for ind, x in enumerate(excess_in_pat)]
            excess_ed_nurses = []
            total_ed_in = sum(new_excess_in_pat)
            for i in new_excess_in_pat:
                excess_ed_nurses.append(i / float(total_ed_in))
            allocation1 = round_standard(excess_ed_nurses, allocatable)
            allocation = [allocation1[i] + reserved_nurses[i] for i in range(4)]
        else:
            total_ed_in = sum(excess_in_pat)
            nurses_new = form.numnurse.data - total_ed_in
            new_reserved_nurses = [max(0, reserved_nurses[ind] - x) for ind, x in enumerate(excess_in_pat)]
            allocation1, unrounded_allocation = heuristic_empty(x_bar, new_reserved_nurses, 12.0, 19, w_mu,
                                                                [optA[0] / nurses, optB[0] / nurses,
                                                                 optC[0] / nurses, optU[0] / nurses],
                                                                norm_b, g, ded, nurses_new)
            allocation = [allocation1[i] + excess_in_pat[i] for i in range(4)]
        # Create data row
        row = [strftime("%Y-%m-%d %H:%M:%S", localtime()), form.dt.data, 'AM',
               form.nursetopat.data, n_to_pat, form.numnurse.data, ed_nurses]
        row += ex_pat + in_pat + allocation + edin_alloc
        # Create storage file if it doesn't exist, otherewise write to file
        if not os.path.exists(os.getcwd() + '/census_data.csv'):
            with open('census_data.csv', 'w') as fil:
                r = csv.writer(fil)
                header = ['date_of_input', 'date', 'shift', 'nurse_patient_ratio_ED', 'nurse_patient_ratio_EDIN',
                          'ED_nurses', 'EDIN_nurses', ' ED_Patients_A', 'ED_Patients_B',
                          'ED_Patients_C', 'ED_Patients_U', 'Inpatient_A', 'Inpatient_B', 'Inpatient_C', 'Nurse_Alloc_A',
                          'Nurse_Alloc_B', 'Nurse_Alloc_C', 'Nurse_Alloc_U', 'EDIN_A', 'EDIN_B', 'EDIN_C']
                r.writerow(header)
                r.writerow(row)
        else:
            with open('census_data.csv', 'a') as fil:
                r = csv.writer(fil)
                r.writerow(row)
        # Get information of new page
        curr_page = 'view_return.html'
        curr_form = None
        result = [[7], ['Bay A:', int(allocation[0])], ['Bay B:', int(allocation[1])],
                      ['Bay C:', int(allocation[2])], ['Bay D:', int(allocation[3])],
                      ['Bay A EDIN:', int(edin_alloc[0])], ['Bay B EDIN:', int(edin_alloc[1])],
                      ['Bay C EDIN:', int(edin_alloc[2])], ['7 AM Shift']]
    else:
        curr_page = 'census_form_am.html'
        curr_form = form
        result = None

    return render_template(curr_page, form=curr_form, result=result)

@app.route('/census_form_pm', methods=['GET', 'POST'])
def census_form_PM():
    form = InputForm_census_PM(request.form)
    if request.method == 'POST' and form.validate():
        # Load necessary data
        optA = [2.15417, -0.5621]
        optB = [2.2625, -0.7571]
        optC = [2.075, -0.5468]
        optU = [2.49025, -0.5141]
        p = [0.45, 0.36, 0.45]
        A_AM = [2.56, 2.73, 2.45]
        A_PM = [1.75, 1.79, 1.70]
        ded = [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0]
        g = [12.0, 12.0, 12.0]
        b = [optA[1], optB[1], optC[1]]
        # Get data from form
        nurses = form.nursetopat.data * form.numnurse.data  # Number of nurses
        n_to_pat = form.nursetopat_2.data  # Nurse to patient ratio
        ed_nurses = form.numnurse_2.data  # EDIN nurses
        if 2 < form.numnurse.data < 8:
            reserved_nurses = [1, 1, 1]
        elif form.numnurse.data <= 2:
            reserved_nurses = [0, 0, 0]
        else:
            reserved_nurses = [4, 2, 2]
        service_rates = [6.767, 6.033, 6.983]  # Service Rates for patients
        w_mu = [1 / s for s in service_rates]  # Average service time
        norm_b = [x / float(nurses) for x in b]  # Normed b value
        # Current number of patients waiting
        ex_pat = [form.currnum1.data, form.currnum2.data, form.currnum3.data]
        x_bar = [x / float(nurses) for x in ex_pat]
        # Current number of inpatients
        in_pat = [form.currnum1_2.data, form.currnum2_2.data, form.currnum3_2.data]
        # Calculated inpatients for the period
        in_pat_tot = [x + p[ind] * (ex_pat[ind] + A_AM[ind]) for ind, x in enumerate(in_pat)]
        in_pat_load = [x / float(sum(in_pat_tot)) for x in in_pat_tot]
        # Divides EDIN nurses proportional to inpatients
        edin_alloc = round_standard(in_pat_load, ed_nurses)
        # Finds excess inpatients after allocating EDIN nurses
        excess_in_pat = []
        allocatable = form.numnurse.data - sum(reserved_nurses)
        extra_nurse_demand = 0
        for ind, x in enumerate(in_pat):
            excess_in_pat.append(np.ceil(max(x - n_to_pat * edin_alloc[ind], 0)/
                            float(n_to_pat)))
            extra_nurse_demand += max(excess_in_pat[ind] - reserved_nurses[ind],0)
        if extra_nurse_demand > allocatable:
            new_excess_in_pat = [max(x - reserved_nurses[ind],0) for ind, x in enumerate(excess_in_pat)]
            excess_ed_nurses = []
            total_ed_in = sum(new_excess_in_pat)
            for i in new_excess_in_pat:
                excess_ed_nurses.append(i / float(total_ed_in))
            allocation1 = round_standard(excess_ed_nurses, allocatable)
            allocation = [allocation1[i] + reserved_nurses[i] for i in range(3)]
        else:
            total_ed_in = sum(excess_in_pat)
            nurses_new = form.numnurse.data - total_ed_in
            new_reserved_nurses = [max(0,reserved_nurses[ind] - x) for ind, x in enumerate(excess_in_pat)]
            allocation1, unrounded_allocation = heuristic_empty(x_bar, new_reserved_nurses, 12.0, 19, w_mu,
                                                                [optA[0] / nurses, optB[0] / nurses,
                                                                 optC[0] / nurses],
                                                                norm_b, g, ded, nurses_new)
            allocation = [allocation1[i] + excess_in_pat[i] for i in range(3)]
        # Create data row
        row = [strftime("%Y-%m-%d %H:%M:%S", localtime()), form.dt.data, 'PM',
               form.nursetopat.data, n_to_pat, form.numnurse.data, ed_nurses]
        ex_pat.append(0)
        allocation.append(0)
        row += ex_pat + in_pat + allocation + edin_alloc
        # Create storage file if it doesn't exist, otherewise write to file
        if not os.path.exists(os.getcwd() + '/census_data.csv'):
            with open('census_data.csv', 'w') as fil:
                r = csv.writer(fil)
                header = ['date_of_input', 'date', 'shift', 'nurse_patient_ratio_ED', 'nurse_patient_ratio_EDIN',
                          'ED_nurses', 'EDIN_nurses', ' ED_Patients_A', 'ED_Patients_B',
                          'ED_Patients_C', 'ED_Patients_U', 'Inpatient_A', 'Inpatient_B', 'Inpatient_C', 'Nurse_Alloc_A',
                          'Nurse_Alloc_B', 'Nurse_Alloc_C', 'Nurse_Alloc_U', 'EDIN_A', 'EDIN_B', 'EDIN_C']
                r.writerow(header)
                r.writerow(row)
        else:
            with open('census_data.csv', 'a') as fil:
                r = csv.writer(fil)
                r.writerow(row)
                # Get information of new page
        curr_page = 'view_return.html'
        curr_form = None
        result = [[19], ['Bay A:', int(allocation[0])], ['Bay B:', int(allocation[1])],
                      ['Bay C:', int(allocation[2])], ['Bay D:', int(allocation[3])],
                      ['Bay A EDIN:', int(edin_alloc[0])], ['Bay B EDIN:', int(edin_alloc[1])],
                      ['Bay C EDIN:', int(edin_alloc[2])], ['7 PM Shift']]
    else:
        curr_page = 'census_form_pm.html'
        curr_form = form
        result = None

    return render_template(curr_page, form=curr_form, result=result)

def func(t,a,b):
    return a + b * np.sin(np.pi * t/12)

if __name__ == '__main__':
    app.run(debug=True)
