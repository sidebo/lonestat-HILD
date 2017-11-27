#!/usr/bin/env python


'''
  Test script to make figures of salary data obtained from Goteborg university
  HILD data base http://es.handels.gu.se/avdelningar/avdelningen-for-ekonomisk-historia/historiska-lonedatabasen-hild/tabeller

  @ Author Edvin Sidebo, edvin.sidebo@cern.ch

'''

import pyexcel_xls
import matplotlib.pyplot as plt
import os
import sys
import json
import pprint as pp
import numpy as np

g_inputFile = "tjansteman_privatsektor_1518916_wcw_1929-1990.xls"
# g_inputFile = "test.xls" #tjansteman_privatsektor_1518916_wcw_1929-1990.xls"
g_outputdir = "./plots/"
g_DEBUG = False #True

##### settings for spreadsheet data: column indices for men, women, etc.
col_idx_men = {"nEmployed": 2, "avgSalary": 4}
col_idx_women = {"nEmployed": 3, "avgSalary": 5}
col_idx_total = {"avgSalary": 6}
#####


# class JobCategory:
#   def __init__(self, name, ):
#     self.name =

############ jobs
g_jobs = {"Teknisk personal": ["samtliga"],
          "Kontorspersonal": ["samtliga"],
          "Butikspersonal": []
          #...
          }
########

def ERROR(msg):
  print("*** ERROR :: {}. Exiting.".format(msg))
  sys.exit(0)


def getYearsArr(keys):
  ''' takes list of keys in string format, returns array of years '''
  if g_DEBUG:
    print("\n*** Inside fcn getYearsArr")
    print("*** Keys passed: ")
    pp.pprint(keys)
    print("")
  return np.array(keys, dtype='int')

def getSalaries(data, job, col_idx, year_low, year_up):
  ''' get dictionary with salaries, salary taken from column determined by col_idx '''

  # dictionary with salaries, on form {year1: salary1, year2: salary2, ...}
  salaries = {}

  # loop over years (spreadsheets)
  for year in data:
    if year_low != -99 and int(year) < year_low:
      continue
    if year_up != -99 and int(year) > year_up:
      break

    data_year = data[year] # list of lists, where every element is a row in the sheet
    # loop over rows in spreadsheet
    for i_row,row in enumerate(data_year):
      if not row:
        continue # skip empty rows
      # if first element has job title, we're at the correct row
      if row[0].startswith(job):
        if g_DEBUG: print("*** Found row with data for year {}, job {}: salary = {}".format(year, job, row[col_idx]))
        if len(row) <= col_idx: # for example col_idx=2, len(row) must be 3 or longer
          ERROR("Inside getSalaries :: nr of columns smaller than expected! data_sheet no = {}, col_idx == {}, len(row) == {}".format(year, col_idx, len(row)))
        try:
          year_int = int(year)
        except ValueError:
          ERROR("Inside getSalaries :: couldn't convert year to int. year = {}, job = {}, col_idx = {}".format(year, job, col_idx) )
        try:
          salary = int(row[col_idx])
        except ValueError:
          try:

            # seems sometimes women's data isn't filled for "Samtliga". See e.g. 1932, women's average salary.
            # take the next row which seems to be the correct number (just for some reason not filled for this row)
            salary = int(data_year[i_row+1][col_idx])
          except ValueError:
            ERROR("Inside getSalaries :: couldn't convert year or salary to int. year = {}, salary = {}, job = {}, col_idx = {}".format(year, row[col_idx], job, col_idx) )

        salaries[year_int] = salary
        break # go to next year

  # return dictionary
  return salaries

def makeTrendPlots(data, year_low=-99, year_up=-99):
  ''' make trend plots over time '''

  #### compare men with women

  for job in g_jobs:
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # get salary for men
    salary_men = getSalaries(data,  job, col_idx_men["avgSalary"], year_low, year_up)
    salary_women = getSalaries(data, job,  col_idx_women["avgSalary"], year_low, year_up)
    salary_tot = getSalaries(data, job,  col_idx_total["avgSalary"], year_low, year_up)

    # check that years are the same in all dictionaries
    diff_menwomen =  set(salary_men.keys()) - set(salary_women.keys())
    if diff_menwomen: # if not empty
      ERROR("Inside makeTrendPlots :: Nr of years don't match in men and women data salary dictionaries!")
    diff_mentotal = set(salary_men.keys()) - set(salary_tot.keys())
    if diff_mentotal: # if not empty
      ERROR("Inside makeTrendPlots :: Nr of years don't match in men and [men+women] data salary dictionaries!")


    plt.plot(salary_men.keys(), salary_men.values(), 'ro', label="Men")
    plt.plot(salary_women.keys(), salary_women.values(), 'g^', label="Women")
    plt.plot(salary_tot.keys(), salary_tot.values(), 'bs', label="All")
    # legend
    plt.legend(numpoints=1, frameon=False, loc="lower right")
    # axis limits
    plt.xlim(salary_men.keys()[0] - 5, salary_men.keys()[-1] + 5)
    plt.ylim(min(salary_women.values())-300, max(salary_men.values())+300)
    # axis labels
    plt.ylabel("Average salary (kr)")
    plt.xlabel("Year")
    # text on plot
    ax.text(0.1, 0.9, job, transform=ax.transAxes )
    # save
    plt.savefig(g_outputdir + "Men-vs-women-" + job.replace(" ", "") + ".png")
    print("\n*** DONE plotting salary data for job {}".format(job))

    #plt.show()


def main(data):
  ''' main fcn '''

  year_low = -99 # -99 will trigger smallest year possible
  year_up = 1946 # the spreadsheets look different after this year
  makeTrendPlots(data, year_low, year_up)

if __name__ == "__main__":

  print("\n*** This script will plot salary data.")

  if not os.path.isfile(g_inputFile):
    ERROR("Couldn't file file {}".format(g_inputFile))

  data = pyexcel_xls.get_data(g_inputFile) # this is an OrderedDict
  # data_str = json.dumps(data) # a long string

  # pp.pprint(data)
  # pp.pprint(data.keys())

  main(data)
  # pp.pprint(foo.keys()) #["Sheet 1"])


  # print(data)
  #print(json.dumps(data)["1929"])
